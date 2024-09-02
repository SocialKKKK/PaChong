from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import subprocess
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # 用于闪存消息

# 用户信息
users = {
    'admin': 'password',
    'root': '123456789'
}

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username in users and users[username] == password:
            session['username'] = username
            return redirect(url_for('dashboard'))
        else:
            return render_template('login.html', error='Invalid Credentials')
    return render_template('login.html')

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'username' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        position = request.form['position']
        try:
            subprocess.run(['python', '智联招聘2.py', position], check=True)
            return jsonify({'status': 'success', 'message': '爬虫已成功运行'})
        except subprocess.CalledProcessError as e:
            return jsonify({'status': 'error', 'message': f'运行爬虫时出错: {e}'})
    return render_template('dashboard.html')

@app.route('/run_data_analysis')
def run_data_analysis():
    if 'username' not in session:
        return redirect(url_for('login'))
    try:
        subprocess.run(['python', 'DataAnalysis.py'], check=True)
        return jsonify({'status': 'success'})
    except subprocess.CalledProcessError as e:
        return jsonify({'status': 'error', 'message': f'运行数据分析时出错: {e}'})

@app.route('/analysis')
def analysis():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('analysis.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
