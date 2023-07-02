import requests 
import json
import pdfkit 
import datetime
import os
import pyrebase
import string
import time
import random

from flask import Flask, render_template, request, redirect, flash, url_for, session

from flask_session import Session
from datetime import timedelta



app = Flask(__name__)
app.secret_key = 'secret'
app.config['UPLOAD_FOLDER'] = 'files'
app.config['SESSION_TYPE'] ='filesystem'
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_USER_SIGNER'] = True
app.config['SESSION_COOKIE_SECURE'] = True
app.config['PERMANET_SESSION_LIFETIME'] = timedelta(minutes=5)

Session(app)

config ={
    'apiKey': "AIzaSyCuATOltNI_Vxu_ucfzXPNmN2V1puvqABU",
    'authDomain': "appweb-orion-php.firebaseapp.com",
    'databaseURL': "https://appweb-orion-php-default-rtdb.firebaseio.com",
    'projectId': "appweb-orion-php",
    'storageBucket': "appweb-orion-php.appspot.com",
    'messagingSenderId': "365589111987",
    'appId': "1:365589111987:web:cc51e2470cbe43ec40fcc6"
}


firebase = pyrebase.initialize_app(config)
auth = firebase.auth()

app.secret_key = 'secret'

# URL do banco de dados do firebase
url = "https://appweb-orion-php-default-rtdb.firebaseio.com/members.json"

# ======================== session user ==============================================================================

# login session 
@app.route("/", methods=["POST", "GET"])
def login():
    if('user' in session):
        return redirect(url_for('read'))

    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        try:

            user = auth.sign_in_with_email_and_password(email, password)
            session['user'] = email
            return redirect(url_for('read'))
        except:
            flash('Failed to login','danger')
            time.sleep(5)
            return flash('Failed to login','danger')
    return render_template("index.html")

# logout session    
@app.route("/logout")
def logout():
    session.pop('user', None)
    session.clear()
    return redirect(url_for('login'))

#============================ Funções de configuração ===========================================================================================

# gerar id automaticamente
def generate_id():
    characters = string.ascii_uppercase + string.digits
    id = ''.join(random.choices(characters, k=16))
    return id

# verificar se o id gerado já existe
def check_id_exists(id):
    # Fazer a solicitação GET para obter os daods do nó "members"
    response = requests.get(f'{url}/members.json')

    if response.status_code == 200:
    
        # Verificar se o id já existe no nó membros
        members = response.json()
        if members:
            for member_id in members:
                if members[member_id]['key'] == id:
                    return True
    return False

# ======================== Funções CRUD para Membros ==============================================================================
# Rota para exibir os dados
@app.route("/read")
def read():
    # verificar se o usuário está autenticado
    if 'user' not in session:
        return redirect(url_for('login'))

    data = read_data()
    return render_template('read.html', data=data)

# Rota para adicionar dados
@app.route('/add', methods=['GET','POST'])
def add():
    if request.method == 'POST':
        nome = request.form['nome']
        pai = request.form['pai']
        mae =  request.form['mae']
        data_nasc = request.form['data_nasc']
        estado_civil = request.form['estado_civil']
        cpf = request.form['cpf']
        rg = request.form['rg']
        setor_atual = request.form['setor_atual']
        igreja_atual = request.form['igreja_atual']
        setor_anterior = request.form['setor_anterior']
        igreja_anterior = request.form['igreja_anterior']
        batizado_com_espirito_santo = request.form['batizado_com_espirito_santo']
        escolaridade = request.form['escolaridade']
        profissao = request.form['profissao']
        batizado = request.form['batizado']
        data_batismo = request.form['data_batismo']
        igreja_de_batismo = request.form['igreja_de_batismo']
        admitido_por = request.form['admitido_por']
        data_da_consagracao = request.form['data_da_consagracao']
        data_da_apresentacao = request.form['data_da_apresentacao']
        cargo_na_igreja = request.form['cargo_na_igreja']
        endereco = request.form['endereco']
        bairro = request.form['bairro']
        cidade = request.form['cidade']
        estado = request.form['estado']
        cep = request.form['cep']
        telefone = request.form['telefone']
        email = request.form['email']
        tem_cartao = request.form['tem_cartao']
        foto = request.files['foto']
        

        # Salvar a imagem em um diretorio local
        # Criar diretorio com nome do membro
        nome_less = nome.replace(" ","")
        dir_membro = os.path.join('static', 'files', nome_less) 
        os.makedirs(dir_membro, exist_ok=True)

        # Salvar Imagem
        imagem_path = os.path.join(dir_membro, nome_less + '.png')
        foto.save(imagem_path)

        # Salvar os dados no firebase
        data = {'nome':nome, 'pai':pai,'mae':mae, 'data_nasc':data_nasc, 'estado_civil':estado_civil, 'cpf':cpf, 'rg':rg,'setor_atual':setor_atual, 'igreja_atual':igreja_atual, 'setor_anterior':setor_anterior, 'igreja_anterior':igreja_anterior, 'batizado_com_espirito_santo':batizado_com_espirito_santo, 'escolaridade':escolaridade, 'profissao':profissao,'batizado':batizado,'data_batismo':data_batismo, 'igreja_de_batismo':igreja_de_batismo, 'admitido_por':admitido_por, 'data_da_consagracao':data_da_consagracao, 'data_da_apresentacao':data_da_apresentacao, 'cargo_na_igreja':cargo_na_igreja, 'endereco':endereco, 'bairro':bairro, 'cidade':cidade, 'estado':estado, 'cep':cep, 'telefone':telefone, 'email':email, 'tem_cartao':tem_cartao, 'foto': imagem_path }
        create_data(data)

        # Exibir mensagem de flash
        flash("Dados cadastrados com sucesso.","success")

        return redirect(url_for('read'))
    return render_template('add.html')


# Rota para editar dados      
@app.route('/edit/<key>', methods=['GET', 'POST'])
def edit(key):
    if request.method == "POST":
        new_nome = request.form['nome']
        new_pai = request.form['pai']
        new_mae =  request.form['mae']
        new_data_nasc = request.form['data_nasc']
        new_estado_civil = request.form['estado_civil']
        new_cpf = request.form['cpf']
        new_rg = request.form['rg']
        new_setor_atual = request.form['setor_atual']
        new_igreja_atual = request.form['igreja_atual']
        new_setor_anterior = request.form['setor_anterior']
        new_igreja_anterior = request.form['igreja_anterior']
        new_batizado_com_espirito_santo = request.form['batizado_com_espirito_santo']
        new_escolaridade = request.form['escolaridade']
        new_profissao = request.form['profissao']
        new_batizado = request.form['batizado']
        new_data_batismo = request.form['data_batismo']
        new_igreja_de_batismo = request.form['igreja_de_batismo']
        new_admitido_por = request.form['admitido_por']
        new_data_da_consagracao = request.form['data_da_consagracao']
        new_data_da_apresentacao = request.form['data_da_apresentacao']
        new_cargo_na_igreja = request.form['cargo_na_igreja']
        new_endereco = request.form['endereco']
        new_bairro = request.form['bairro']
        new_cidade = request.form['cidade']
        new_estado = request.form['estado']
        new_cep = request.form['cep']
        new_telefone = request.form['telefone']
        new_email = request.form['email']
        new_tem_cartao = request.form['tem_cartao']

        new_data = {
            "nome": new_nome,
            "pai": new_pai,
            "mae": new_mae,
            "data_nasc": new_data_nasc,
            "estado_civil": new_estado_civil,
            "cpf": new_cpf,
            "rg": new_rg,
            "setor_atual": new_setor_atual,
            "igreja_atual": new_igreja_atual,
            "setor_anterior": new_setor_anterior,
            "igreja_anterior": new_igreja_anterior,
            "batizado_com_espirito_santo": new_batizado_com_espirito_santo,
            "escolaridade": new_escolaridade,
            "profissao": new_profissao,
            "batizado": new_batizado,
            "data_batismo": new_data_batismo,
            "igreja_de_batismo": new_igreja_de_batismo,
            "admitido_por": new_admitido_por,
            "data_da_consagracao": new_data_da_consagracao,
            "data_da_apresentacao": new_data_da_apresentacao,
            "cargo_na_igreja": new_cargo_na_igreja,
            "endereco": new_endereco,
            "bairro": new_bairro,
            "cidade": new_cidade,
            "estado": new_estado,
            "cep": new_cep,
            "telefone": new_telefone,
            "email": new_email,
            "tem_cartao": new_tem_cartao
        }    

        update_data(key, new_data)
        
        flash("Dados atualizados com sucesso","success")
        return redirect('/read')
    else:
        data = read_data()
        if key in data:
            return render_template("edit.html", key=key, data=data[key])
        else:
            return "Chave Inválida."


# Rota para exibir os dados do membro e gerar o PDF
@app.route("/report/<key>")
def report(key):
   return render_template("index.html")


# Rota para excluir dados
@app.route('/delete/<key>')
def delete(key):
    delete_data(key)
    flash('Dados deletados com sucesso.','success')
    return redirect('/read')


#============================ Funções para os métodos HTTP ===========================================================================================

# Função para criar os dados
def create_data(data):
   
    response = requests.post(url, json.dumps(data))
    if response.status_code != 200:
        print('Erro ao criar dados.')

# Função para ler os dados
def read_data():
   
    response = requests.get(url)
    if response.status_code == 200:
        
        data = response.json()
        return data
    else:
        print('Erro ao ler dados.')
        

# Função para atualizar dados
def update_data(key, new_data):
    url_update = f"https://appweb-orion-php-default-rtdb.firebaseio.com/members/{key}.json"
    response = requests.patch(url_update, json.dumps(new_data))
    if response.status_code != 200:
        print('Erro ao atualizar dados.')

# Função para deletar dados
def delete_data(key):
    url_delete = f"https://appweb-orion-php-default-rtdb.firebaseio.com/membros/{key}.json"
    
    response = requests.delete(url_delete)
    if response.status_code == 200:
        print('Dados excluidos com sucesso.')
        print(key)
        print(url_delete)
    else:
        print('Erro ao excluir dados.')


# Inicialização da aplicação Flask
if __name__=='__main__':
    app.run(debug=True)