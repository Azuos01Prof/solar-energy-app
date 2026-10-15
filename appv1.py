from flask import Flask, render_template, request, jsonify, redirect, url_for
import pandas as pd
import os
import json
from datetime import datetime, timedelta
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import io
import base64
import numpy as np

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['DATA_FOLDER'] = 'data'

# Criar pastas se não existirem
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['DATA_FOLDER'], exist_ok=True)

# Dados iniciais do cliente
cliente_data = {
    'endereco': {
        'rua': 'AV NARA LEAO',
        'numero': '142',
        'bairro': 'RES P TIPUANAS',
        'cep': '14802-835',
        'cidade': 'ARARAQUARA',
        'estado': 'SP'
    },
    'telefone': '',
    'planta': {
        'inversor_marca': '',
        'inversor_modelo': '',
        'inversor_capacidade': '',
        'modulo_marca': '',
        'modulo_modelo': '',
        'modulo_capacidade': '',
        'direcao': '',
        'inclinacao': '',
        'mes_instalacao': '',
        'ano_instalacao': ''
    }
}

def load_monitoracao_data():
    """Carrega dados de monitoração do arquivo CSV"""
    try:
        file_path = os.path.join(app.config['DATA_FOLDER'], 'monitoracao.csv')
        if os.path.exists(file_path):
            df = pd.read_csv(file_path)
            return df.to_dict('records')
    except Exception as e:
        print(f"Erro ao carregar monitoração: {e}")
    
    # Dados padrão vazios
    return []

def load_consumo_data():
    """Carrega dados de consumo do arquivo CSV"""
    try:
        file_path = os.path.join(app.config['DATA_FOLDER'], 'consumo.csv')
        if os.path.exists(file_path):
            df = pd.read_csv(file_path)
            return df.to_dict('records')
    except Exception as e:
        print(f"Erro ao carregar consumo: {e}")
    
    # Dados padrão vazios
    return []

def parse_monitoracao_file(file_content):
    """Parse do arquivo de monitoração"""
    try:
        lines = file_content.strip().split('\n')
        data = []
        
        for line in lines[1:]:  # Pular cabeçalho
            parts = line.split(';')
            if len(parts) >= 4:
                data.append({
                    'ordem': len(data) + 1,
                    'mes_ano': parts[1],
                    'valor': float(parts[3].replace(',', '.'))
                })
        return data
    except Exception as e:
        print(f"Erro no parse: {e}")
        return []

def parse_consumo_file(file_content):
    """Parse da fatura CPFL - simplificado para exemplo"""
    # Esta função precisaria ser adaptada para o formato real do PDF
    # Aqui é um exemplo simplificado
    try:
        # Dados de exemplo baseados no PDF
        data = [
            {'mes_ano': 'OUT/25', 'consumo': 622, 'injecao': 336},
            {'mes_ano': 'SET/25', 'consumo': 651, 'injecao': 0},
            {'mes_ano': 'AGO/25', 'consumo': 755, 'injecao': 0},
            # Adicione mais meses conforme necessário
        ]
        return data
    except Exception as e:
        print(f"Erro no parse consumo: {e}")
        return []

@app.route('/')
def index():
    return redirect(url_for('cliente'))

@app.route('/cliente', methods=['GET', 'POST'])
def cliente():
    global cliente_data
    
    if request.method == 'POST':
        # Atualizar dados do cliente
        cliente_data['endereco'] = {
            'rua': request.form.get('rua', ''),
            'numero': request.form.get('numero', ''),
            'bairro': request.form.get('bairro', ''),
            'cep': request.form.get('cep', ''),
            'cidade': request.form.get('cidade', ''),
            'estado': request.form.get('estado', '')
        }
        cliente_data['telefone'] = request.form.get('telefone', '')
        
        cliente_data['planta'] = {
            'inversor_marca': request.form.get('inversor_marca', ''),
            'inversor_modelo': request.form.get('inversor_modelo', ''),
            'inversor_capacidade': request.form.get('inversor_capacidade', ''),
            'modulo_marca': request.form.get('modulo_marca', ''),
            'modulo_modelo': request.form.get('modulo_modelo', ''),
            'modulo_capacidade': request.form.get('modulo_capacidade', ''),
            'direcao': request.form.get('direcao', ''),
            'inclinacao': request.form.get('inclinacao', ''),
            'mes_instalacao': request.form.get('mes_instalacao', ''),
            'ano_instalacao': request.form.get('ano_instalacao', '')
        }
    
    return render_template('cliente.html', cliente=cliente_data)

@app.route('/tabelas')
def tabelas():
    monitoracao_data = load_monitoracao_data()
    consumo_data = load_consumo_data()
    
    # Organizar dados em formato de tabela
    monitoracao_table = organize_monitoracao_table(monitoracao_data)
    consumo_table, injecao_table = organize_consumo_table(consumo_data)
    
    return render_template('tabelas.html', 
                         monitoracao=monitoracao_table,
                         consumo=consumo_table,
                         injecao=injecao_table)

@app.route('/graficos')
def graficos():
    monitoracao_data = load_monitoracao_data()
    consumo_data = load_consumo_data()
    
    # Gerar gráfico
    chart_url = generate_scatter_plot(monitoracao_data, consumo_data)
    
    return render_template('graficos.html', chart_url=chart_url)

@app.route('/referencias')
def referencias():
    return render_template('referencias.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    file_type = request.form.get('file_type')
    file = request.files.get('file')
    
    if file and file.filename:
        filename = file.filename
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Processar arquivo baseado no tipo
        if file_type == 'monitoracao':
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            data = parse_monitoracao_file(content)
            # Salvar dados processados
            df = pd.DataFrame(data)
            df.to_csv(os.path.join(app.config['DATA_FOLDER'], 'monitoracao.csv'), index=False)
        
        elif file_type == 'consumo':
            # Processar consumo (simplificado)
            data = parse_consumo_file("")  # Implementar parse real
            df = pd.DataFrame(data)
            df.to_csv(os.path.join(app.config['DATA_FOLDER'], 'consumo.csv'), index=False)
    
    return redirect(url_for('tabelas'))

@app.route('/update_table', methods=['POST'])
def update_table():
    table_type = request.form.get('table_type')
    data = request.get_json()
    
    if table_type == 'monitoracao':
        df = pd.DataFrame(data)
        df.to_csv(os.path.join(app.config['DATA_FOLDER'], 'monitoracao.csv'), index=False)
    elif table_type == 'consumo':
        df = pd.DataFrame(data)
        df.to_csv(os.path.join(app.config['DATA_FOLDER'], 'consumo.csv'), index=False)
    
    return jsonify({'status': 'success'})

def organize_monitoracao_table(data):
    """Organiza dados de monitoração em formato de tabela 5x12"""
    table = {}
    
    for item in data:
        mes_ano = item['mes_ano']
        if '/' in mes_ano:
            ano, mes = mes_ano.split('/')
            if ano not in table:
                table[ano] = [''] * 12
            table[ano][int(mes)-1] = item['valor']
    
    return table

def organize_consumo_table(data):
    """Organiza dados de consumo e injeção em formato de tabela"""
    consumo_table = {}
    injecao_table = {}
    
    for item in data:
        mes_ano = item['mes_ano']
        if '/' in mes_ano:
            mes, ano = mes_ano.split('/')
            full_ano = '20' + ano  # Assumindo anos 2000+
            
            if full_ano not in consumo_table:
                consumo_table[full_ano] = [''] * 12
                injecao_table[full_ano] = [''] * 12
            
            # Converter mês abreviado para número
            meses = {
                'JAN': 0, 'FEV': 1, 'MAR': 2, 'ABR': 3, 'MAI': 4, 'JUN': 5,
                'JUL': 6, 'AGO': 7, 'SET': 8, 'OUT': 9, 'NOV': 10, 'DEZ': 11
            }
            
            if mes in meses:
                consumo_table[full_ano][meses[mes]] = item.get('consumo', '')
                injecao_table[full_ano][meses[mes]] = item.get('injecao', '')
    
    return consumo_table, injecao_table

def generate_scatter_plot(monitoracao_data, consumo_data):
    """Gera gráfico de dispersão"""
    try:
        # Preparar dados
        geracao = [item['valor'] for item in monitoracao_data if item['valor'] > 0]
        meses_validos = [i for i, item in enumerate(monitoracao_data) if item['valor'] > 0]
        
        if not geracao:
            return None
        
        # Calcular médias
        media_geracao = np.mean(geracao)
        
        plt.figure(figsize=(10, 6))
        
        # Gráfico de dispersão
        plt.scatter(meses_validos, geracao, alpha=0.7, label='Geração Mensal')
        
        # Linha da média
        plt.axhline(y=media_geracao, color='r', linestyle='--', 
                   label=f'Média: {media_geracao:.2f} kWh')
        
        plt.xlabel('Meses (apenas com geração)')
        plt.ylabel('Geração (kWh)')
        plt.title('Dispersão da Geração de Energia Solar')
        plt.legend()
        plt.grid(True, alpha=0.3)
        
        # Converter para base64
        img = io.BytesIO()
        plt.savefig(img, format='png', bbox_inches='tight')
        img.seek(0)
        chart_url = base64.b64encode(img.getvalue()).decode()
        plt.close()
        
        return f"data:image/png;base64,{chart_url}"
    
    except Exception as e:
        print(f"Erro ao gerar gráfico: {e}")
        return None

if __name__ == '__main__':
    app.run(debug=True)