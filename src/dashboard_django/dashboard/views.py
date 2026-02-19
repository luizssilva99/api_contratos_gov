"""
Views do Dashboard GovAnalytics.
"""
import json
import math
from datetime import datetime

import pandas as pd
from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import redirect, render

from .data_loader import get_data_metadata, load_data
from .models import UserProfile


def login_view(request):
    """Tela de login."""
    if request.user.is_authenticated:
        return redirect('dashboard')

    error = None
    if request.method == 'POST':
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            # Create profile if it doesn't exist
            UserProfile.objects.get_or_create(user=user)
            next_url = request.GET.get('next', '/')
            return redirect(next_url)
        else:
            error = 'Usuário ou senha inválidos.'

    return render(request, 'login.html', {'error': error})


def logout_view(request):
    """Logout."""
    logout(request)
    return redirect('login')


@login_required
def dashboard_view(request):
    """Renderiza o dashboard principal."""
    # Ensure profile exists
    profile, _ = UserProfile.objects.get_or_create(user=request.user)

    # Pega o nome do primeiro grupo do usuário (gerenciável no admin)
    user_groups = request.user.groups.all()
    group_name = user_groups.first().name if user_groups.exists() else 'Sem Grupo'

    context = {
        'user_display_name': profile.get_display_name(),
        'user_initials': profile.get_initials(),
        'user_department': group_name,
        'data_metadata': get_data_metadata(),
    }
    return render(request, 'dashboard.html', context)


@login_required
def api_data(request):
    """
    API endpoint que retorna dados filtrados em JSON.
    Query params: categoria, departamento, status, ano, uf, fornecedor, data_inicio, data_fim, page, per_page
    """
    df = load_data()
    if df.empty:
        return JsonResponse({'error': 'Dados não encontrados'}, status=404)

    filtered_df = df.copy()

    # Apply filters
    categoria = request.GET.get('categoria', '')
    if categoria and categoria != 'Todos os Serviços':
        filtered_df = filtered_df[filtered_df['tipo_contrato'] == categoria]

    departamento = request.GET.get('departamento', '')
    if departamento and departamento != 'Todos':
        filtered_df = filtered_df[filtered_df['modalidadeCompra'] == departamento]

    status_list = request.GET.getlist('status')
    if status_list:
        filtered_df = filtered_df[filtered_df['situacaoContrato'].isin(status_list)]

    anos = request.GET.getlist('ano')
    if anos:
        anos_int = [int(a) for a in anos if a.isdigit()]
        if anos_int:
            filtered_df = filtered_df[filtered_df['ano_assinatura'].isin(anos_int)]

    ufs = request.GET.getlist('uf')
    if ufs:
        filtered_df = filtered_df[filtered_df['uf_gestora'].isin(ufs)]

    fornecedores = request.GET.getlist('fornecedor')
    if fornecedores:
        filtered_df = filtered_df[filtered_df['nome_fornecedor'].isin(fornecedores)]

    data_inicio = request.GET.get('data_inicio', '')
    data_fim = request.GET.get('data_fim', '')
    if data_inicio and data_fim:
        try:
            d_start = datetime.strptime(data_inicio, '%Y-%m-%d').date()
            d_end = datetime.strptime(data_fim, '%Y-%m-%d').date()
            filtered_df = filtered_df[
                (filtered_df['dataAssinatura'].dt.date >= d_start) &
                (filtered_df['dataAssinatura'].dt.date <= d_end)
            ]
        except (ValueError, TypeError):
            pass

    total_contratos = len(filtered_df)
    valor_total = float(filtered_df['valorInicialCompra'].sum()) if total_contratos > 0 else 0

    # KPI calculations
    pct_bens = 0
    pct_servicos = 0
    if total_contratos > 0:
        bens_count = len(filtered_df[filtered_df['tipo_contrato'] == 'Aquisição de Bens'])
        servicos_count = len(filtered_df[filtered_df['tipo_contrato'] == 'Prestação de Serviços'])
        pct_bens = round((bens_count / total_contratos) * 100, 1)
        pct_servicos = round((servicos_count / total_contratos) * 100, 1)

    # YoY variation
    variacao_yoy = None
    if total_contratos > 0 and 'ano_assinatura' in filtered_df.columns:
        anos_disp = sorted(filtered_df['ano_assinatura'].unique())
        if len(anos_disp) >= 2:
            ultimo = anos_disp[-1]
            penultimo = anos_disp[-2]
            val_ultimo = float(filtered_df[filtered_df['ano_assinatura'] == ultimo]['valorInicialCompra'].sum())
            val_penultimo = float(filtered_df[filtered_df['ano_assinatura'] == penultimo]['valorInicialCompra'].sum())
            if val_penultimo > 0:
                variacao_yoy = round(((val_ultimo - val_penultimo) / val_penultimo) * 100, 1)

    # Chart data: distribution by type
    tipo_counts = {}
    if total_contratos > 0:
        tc = filtered_df['tipo_contrato'].value_counts()
        tipo_counts = {str(k): int(v) for k, v in tc.items()}

    # Chart data: top UFs
    uf_top = []
    if total_contratos > 0:
        uf_data = filtered_df['uf_gestora'].value_counts().head(5)
        uf_top = [{'uf': str(k), 'count': int(v)} for k, v in uf_data.items()]

    # Chart data: evolution (use FULL df, not filtered)
    evolution = []
    if not df.empty and 'ano_assinatura' in df.columns:
        yearly = df['ano_assinatura'].value_counts().sort_index()
        evolution = [{'ano': int(k), 'qtd': int(v)} for k, v in yearly.items()]

    # Table data (paginated)
    page = int(request.GET.get('page', 1))
    per_page = int(request.GET.get('per_page', 25))  # Default 25 as requested
    total_pages = max(1, math.ceil(total_contratos / per_page))
    page = min(page, total_pages)

    start_idx = (page - 1) * per_page
    end_idx = start_idx + per_page

    # Use ALL available columns for the table slice (for detailed view)
    available_cols = list(filtered_df.columns)
    table_slice = filtered_df.iloc[start_idx:end_idx][available_cols].copy()

    # Calculate days until end of vigência before formatting dates
    today = datetime.now().date()
    dias_vigencia_list = []
    if 'dataFimVigencia' in table_slice.columns:
        for val in table_slice['dataFimVigencia']:
            if pd.notnull(val):
                try:
                    dias = (val.date() - today).days if hasattr(val, 'date') else (val - today).days
                    dias_vigencia_list.append(dias)
                except Exception:
                    dias_vigencia_list.append(None)
            else:
                dias_vigencia_list.append(None)
    else:
        dias_vigencia_list = [None] * len(table_slice)

    # Calculate difference (Final - Initial)
    diferenca_list = []
    if 'valorFinalCompra' in table_slice.columns and 'valorInicialCompra' in table_slice.columns:
        for idx, row in table_slice.iterrows():
            try:
                vi = row['valorInicialCompra']
                vf = row['valorFinalCompra']
                if pd.notnull(vi) and pd.notnull(vf):
                    val_i = float(vi)
                    val_f = float(vf)
                    diff = val_f - val_i
                    diferenca_list.append(diff if diff != 0 else None)
                else:
                    diferenca_list.append(None)
            except Exception:
                diferenca_list.append(None)
    else:
        diferenca_list = [None] * len(table_slice)

    # Format dates and values for JSON
    date_cols = ['dataAssinatura', 'dataInicioVigencia', 'dataFimVigencia', 'dataPublicacaoDOU']
    for col in date_cols:
        if col in table_slice.columns:
            table_slice[col] = table_slice[col].apply(
                lambda x: x.strftime('%d/%m/%Y') if pd.notnull(x) else '-'
            )

    table_records = table_slice.fillna('-').to_dict('records')
    # Add calculated fields to each record
    for i, rec in enumerate(table_records):
        rec['dias_vigencia'] = dias_vigencia_list[i]
        rec['diferenca_valor'] = diferenca_list[i]

    # Ensure floats are serializable
    for rec in table_records:
        for k, v in rec.items():
            if isinstance(v, float):
                rec[k] = round(v, 2)

    # Filter options (for sidebar dropdowns)
    filter_options = {
        'categorias': sorted(df['tipo_contrato'].dropna().unique().tolist()),
        'departamentos': sorted(df['modalidadeCompra'].dropna().unique().tolist()),
        'statuses': sorted(df['situacaoContrato'].dropna().unique().tolist()),
        'anos': sorted([int(a) for a in df['ano_assinatura'].dropna().unique()], reverse=True),
        'ufs': sorted(df['uf_gestora'].dropna().unique().tolist()),
    }

    # Export data (all filtered, all columns)
    export_cols = ['id', 'numero', 'nome_fornecedor', 'objeto', 'valorInicialCompra',
                   'valorFinalCompra', 'situacaoContrato', 'modalidadeCompra',
                   'tipo_contrato', 'uf_gestora', 'ano_assinatura',
                   'dataAssinatura', 'dataInicioVigencia', 'dataFimVigencia']
    export_available = [c for c in export_cols if c in filtered_df.columns]

    export_data = filtered_df[export_available].copy()
    for col in ['dataAssinatura', 'dataInicioVigencia', 'dataFimVigencia']:
        if col in export_data.columns:
            export_data[col] = export_data[col].apply(
                lambda x: x.strftime('%d/%m/%Y') if pd.notnull(x) else ''
            )

    export_records = export_data.fillna('').to_dict('records')
    for rec in export_records:
        for k, v in rec.items():
            if isinstance(v, float):
                rec[k] = round(v, 2)

    response = {
        'kpis': {
            'total_contratos': total_contratos,
            'valor_total': valor_total,
            'pct_bens': pct_bens,
            'pct_servicos': pct_servicos,
            'variacao_yoy': variacao_yoy,
        },
        'charts': {
            'tipo_distribuicao': tipo_counts,
            'uf_top': uf_top,
            'evolucao': evolution,
        },
        'table': {
            'records': table_records,
            'columns': available_cols,
            'page': page,
            'per_page': per_page,
            'total_pages': total_pages,
            'total_records': total_contratos,
        },
        'filter_options': filter_options,
        'export_data': export_records,
        'metadata': get_data_metadata(),
        'total_registros_base': len(df),
    }

    return JsonResponse(response, safe=False)
