import uuid
import requests
from flask import Flask, render_template, session, request, redirect, url_for, redirect, send_file, Response, make_response
from flask_session import Session  # https://pythonhosted.org/Flask-Session
import msal
import app_config
import redshift_connector
import pandas as pd
from datetime import date
import jwt
import datetime
import uuid

today=str(date.today())

app = Flask(__name__)
app.config.from_object(app_config)
Session(app)

# This section is needed for url_for("foo", _external=True) to automatically
# generate http scheme when this sample is running on localhost,
# and to generate https scheme when it is deployed behind reversed proxy.
# See also https://flask.palletsprojects.com/en/1.0.x/deploying/wsgi-standalone/#proxy-setups
from werkzeug.middleware.proxy_fix import ProxyFix
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

@app.route("/" ,methods=['GET', 'POST'])
def index():
    if not session.get("user"):
        return redirect(url_for("login"))
    if request.method == 'POST':
        var = request.form.to_dict(flat=False)
        query=''
        insert=''
        if var['db'][0]=='Annual':
            if len(var['year'])==1:
                query=(f'''select count(*) from {var['state'][0]}_ann where substring(CAST(CurrentSalerecordingDate as Varchar),0,5)='{var['year'][0][1:5]}' and ConcurrentMtg1Lender LIKE '%{var['comp'][0].upper()}%' and ConcurrentMtg1LoanAmt<{var['mtg'][0]};''')
            else:
                for i in range(len(var['year'])):
                    if i!=len(var['year'])-1:
                        insert+=(f'''substring(CAST(CurrentSalerecordingDate as Varchar),0,5)='{var['year'][i][1:5]}' or  ''')
                    else:
                        insert+=(f'''substring(CAST(CurrentSalerecordingDate as Varchar),0,5)='{var['year'][i][1:5]}') ''')
                query=(f'''select count(*) from {var['state'][0]}_ann where ({insert}  and ConcurrentMtg1Lender LIKE '%{var['comp'][0].upper()}%' and ConcurrentMtg1LoanAmt<{var['mtg'][0]};''')
        else:
            if len(var['year'])==1:
                    query=(f'''select count(*) from {var['state'][0]}_deed where substring(CAST(RecordingDate as Varchar),0,5)='{var['year'][0][1:5]}' and FirstMtgLenderName LIKE '%{var['comp'][0].upper()}%' and FirstMtgAmt<{var['mtg'][0]};''')
            else:
                for i in range(len(var['year'])):
                    if i!=len(var['year'])-1:
                        insert+=(f''' substring(CAST(RecordingDate as Varchar),0,5)='{var['year'][i][1:5]}' or ''')
                    else:
                       insert+=(f''' substring(CAST(RecordingDate as Varchar),0,5)='{var['year'][i][1:5]}') ''')
                query=(f'''select count(*) from {var['state'][0]}_deed where ({insert} and FirstMtgLenderName LIKE '%{var['comp'][0].upper()}%' and FirstMtgAmt<{var['mtg'][0]};''')
        session['my_var'] = var
        with redshift_connector.connect(  host='redshift-cluster-1.c5tkeodvepns.us-west-2.redshift.amazonaws.com',
            port=5439,
            database='dev',
            user='awsuser',
            password='Awspassword12345') as conn:
            with conn.cursor() as cursor:
                cursor.execute(query)
                result1= cursor.fetchall()
        print(query)
        p=('The Current Query has '+str(result1[0][0])+' Rows')
        return render_template('index.html',p=p,date=today,user=session["user"], version=msal.__version__)
    elif request.method=='GET':
        return render_template("index.html",date=today,user=session["user"], version=msal.__version__)
    return render_template('index.html', date=today,user=session["user"], version=msal.__version__)


@app.route("/get-file")
def get_file():
    var = session.get('my_var', None)
    query=''
    insert=''
    if var['db'][0]=='Annual':
        if len(var['year'])==1:
            query=(f'''select * from {var['state'][0]}_ann where substring(CAST(CurrentSalerecordingDate as Varchar),0,5)='{var['year'][0][1:5]}' and ConcurrentMtg1Lender LIKE '%{var['comp'][0].upper()}%' and ConcurrentMtg1LoanAmt<{var['mtg'][0]};''')
        else:
            for i in range(len(var['year'])):
                if i!=len(var['year'])-1:
                    insert+=(f'''substring(CAST(CurrentSalerecordingDate as Varchar),0,5)='{var['year'][i][1:5]}' or  ''')
                else:
                    insert+=(f'''substring(CAST(CurrentSalerecordingDate as Varchar),0,5)='{var['year'][i][1:5]}') ''')
            query=(f'''select * from {var['state'][0]}_ann where ({insert}  and ConcurrentMtg1Lender LIKE '%{var['comp'][0].upper()}%' and ConcurrentMtg1LoanAmt<{var['mtg'][0]};''')
    else:
        if len(var['year'])==1:
            query=(f'''select * from {var['state'][0]}_deed where substring(CAST(RecordingDate as Varchar),0,5)='{var['year'][0][1:5]}' and FirstMtgLenderName LIKE '%{var['comp'][0].upper()}%' and FirstMtgAmt<{var['mtg'][0]};''')
        else:
            for i in range(len(var['year'])):
                if i!=len(var['year'])-1:
                    insert+=(f''' substring(CAST(RecordingDate as Varchar),0,5)='{var['year'][i][1:5]}' or ''')
                else:
                    insert+=(f''' substring(CAST(RecordingDate as Varchar),0,5)='{var['year'][i][1:5]}') ''')
            query=(f'''select * from {var['state'][0]}_deed where ({insert} and FirstMtgLenderName LIKE '%{var['comp'][0].upper()}%' and FirstMtgAmt<{var['mtg'][0]};''')
    print(query)
    with redshift_connector.connect(  host='redshift-cluster-1.c5tkeodvepns.us-west-2.redshift.amazonaws.com',
     port=5439,
     database='dev',
     user='awsuser',
     password='Awspassword12345') as conn:
        with conn.cursor() as cursor:
            cursor.execute(query)
            result: pd.DataFrame = cursor.fetch_dataframe()            
    resp = make_response(result.to_csv())
    resp.headers["Content-Disposition"] = f"attachment; filename={var['state'][0]}_{var['db'][0]}_{var['comp'][0]}.csv"
    resp.headers["Content-Type"] = "text/csv"
    return resp

@app.route("/owner" ,methods=['GET', 'POST'])
def owner():
    if request.method == 'POST':
        var = request.form.to_dict(flat=False)
        query=''
        insert=''
        insert2=''

        if var['db'][0]=='Annual':
            if var['owntype'][0]=='Corporate':
                insert2='''AND Owner1Corpind='T' '''
            elif var['owntype'][0]=='Individual':
                insert2='''AND Owner1Corpind<>'T' '''
            if len(var['year'])==1:
                query=(f'''select count(*) from {var['state'][0]}_ann where substring(CAST(CurrentSalerecordingDate as Varchar),0,5)='{var['year'][0][1:5]}' and OwnerName1Full LIKE '%{var['comp'][0].upper()}%' and ConcurrentMtg1LoanAmt<{var['mtg'][0]} {insert2};''')
            else:
                for i in range(len(var['year'])):
                    if i!=len(var['year'])-1:
                        insert+=(f'''substring(CAST(CurrentSalerecordingDate as Varchar),0,5)='{var['year'][i][1:5]}' or  ''')
                    else:
                        insert+=(f'''substring(CAST(CurrentSalerecordingDate as Varchar),0,5)='{var['year'][i][1:5]}') ''')
                query=(f'''select count(*) from {var['state'][0]}_ann where ({insert}  and OwnerName1Full LIKE '%{var['comp'][0].upper()}%' and ConcurrentMtg1LoanAmt<{var['mtg'][0]} {insert2};''')
        else:
            if var['owntype'][0]=='Corporate':
                insert2='''AND BuyerBorrower1CorpInd='Y' '''
            elif var['owntype'][0]=='Individual':
                insert2='''AND BuyerBorrower1CorpInd<>'Y' '''
            if len(var['year'])==1:
                    query=(f'''select count(*) from {var['state'][0]}_deed where substring(CAST(RecordingDate as Varchar),0,5)='{var['year'][0][1:5]}' and BuyerBorrower1Name LIKE '%{var['comp'][0].upper()}%' and FirstMtgAmt<{var['mtg'][0]} {insert2};''')
            else:
                for i in range(len(var['year'])):
                    if i!=len(var['year'])-1:
                        insert+=(f''' substring(CAST(RecordingDate as Varchar),0,5)='{var['year'][i][1:5]}' or ''')
                    else:
                       insert+=(f''' substring(CAST(RecordingDate as Varchar),0,5)='{var['year'][i][1:5]}') ''')
                query=(f'''select count(*) from {var['state'][0]}_deed where ({insert} and BuyerBorrower1Name LIKE '%{var['comp'][0].upper()}%' and FirstMtgAmt<{var['mtg'][0]} {insert2};''')
        session['my_var'] = var
        with redshift_connector.connect(  host='redshift-cluster-1.c5tkeodvepns.us-west-2.redshift.amazonaws.com',
            port=5439,
            database='dev',
            user='awsuser',
            password='Awspassword12345') as conn:
            with conn.cursor() as cursor:
                cursor.execute(query)
                result1= cursor.fetchall()
        p=('The Current Query has '+str(result1[0][0])+' Rows')
        return render_template('Owner.html',p=p,date=today,user=session["user"], version=msal.__version__)
    elif request.method=='GET':
        return render_template("Owner.html",date=today,user=session["user"], version=msal.__version__)
    else:
        return render_template("Owner.html",date=today,user=session["user"], version=msal.__version__)


@app.route("/get-file1")
def get_file1():
    var = session.get('my_var', None)
    query=''
    insert=''
    insert2=''
    if var['db'][0]=='Annual':
        if var['owntype'][0]=='Corporate':
            insert2='''AND Owner1Corpind='T' '''
        elif var['owntype'][0]=='Individual':
            insert2='''AND Owner1Corpind<>'T' '''
        if len(var['year'])==1:
            query=(f'''select * from {var['state'][0]}_ann where substring(CAST(CurrentSalerecordingDate as Varchar),0,5)='{var['year'][0][1:5]}' and OwnerName1Full LIKE '%{var['comp'][0].upper()}%' and ConcurrentMtg1LoanAmt<{var['mtg'][0]} {insert2};''')
        else:
            for i in range(len(var['year'])):
                if i!=len(var['year'])-1:
                    insert+=(f'''substring(CAST(CurrentSalerecordingDate as Varchar),0,5)='{var['year'][i][1:5]}' or  ''')
                else:
                    insert+=(f'''substring(CAST(CurrentSalerecordingDate as Varchar),0,5)='{var['year'][i][1:5]}') ''')
            query=(f'''select * from {var['state'][0]}_ann where ({insert}  and OwnerName1Full LIKE '%{var['comp'][0].upper()}%' and ConcurrentMtg1LoanAmt<{var['mtg'][0]} {insert2};''')
    else:
        if var['owntype'][0]=='Corporate':
            insert2='''AND BuyerBorrower1CorpInd='Y' '''
        elif var['owntype'][0]=='Individual':
            insert2='''AND BuyerBorrower1CorpInd<>'Y' '''
        if len(var['year'])==1:
            query=(f'''select * from {var['state'][0]}_deed where substring(CAST(RecordingDate as Varchar),0,5)='{var['year'][0][1:5]}' and BuyerBorrower1Name LIKE '%{var['comp'][0].upper()}%' and FirstMtgAmt<{var['mtg'][0]} {insert2};''')
        else:
            for i in range(len(var['year'])):
                if i!=len(var['year'])-1:
                    insert+=(f''' substring(CAST(RecordingDate as Varchar),0,5)='{var['year'][i][1:5]}' or ''')
                else:
                    insert+=(f''' substring(CAST(RecordingDate as Varchar),0,5)='{var['year'][i][1:5]}') ''')
            query=(f'''select * from {var['state'][0]}_deed where ({insert} and BuyerBorrower1Name LIKE '%{var['comp'][0].upper()}%' and FirstMtgAmt<{var['mtg'][0]} {insert2};''')
    with redshift_connector.connect(  host='redshift-cluster-1.c5tkeodvepns.us-west-2.redshift.amazonaws.com',
     port=5439,
     database='dev',
     user='awsuser',
     password='Awspassword12345') as conn:
        with conn.cursor() as cursor:
            cursor.execute(query)
            result: pd.DataFrame = cursor.fetch_dataframe()            
    resp = make_response(result.to_csv())
    resp.headers["Content-Disposition"] = f"attachment; filename={var['state'][0]}_{var['db'][0]}_Owner_{var['comp'][0]}.csv"
    resp.headers["Content-Type"] = "text/csv"
    return resp

@app.route("/dashboard")
def dash():
    token = jwt.encode(
	{
		"iss": '3af22039-a099-4e37-8c57-f61f5e3344f8',
		"exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=5),
		"jti": str(uuid.uuid4()),
		"aud": "tableau",
		"sub": 'vendoradmin@aureusfg.com',
		"scp": ["tableau:views:embed", "tableau:metrics:embed"]
	},
		'9DuLGdhvcjC6Q++uyDsR6HZISohEPnqXrp6yvuw4334=',
		algorithm = "HS256",
		headers = {
		'kid': 'd56c3869-5df2-42da-a614-42206b0876c9',
		'iss': '3af22039-a099-4e37-8c57-f61f5e3344f8'
        }
    )
    return render_template("dashboard.html",date=today,user=session["user"], jwt=token, version=msal.__version__)

@app.route("/dashboard2")
def dash2():
    token = jwt.encode(
	{
		"iss": '3af22039-a099-4e37-8c57-f61f5e3344f8',
		"exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=5),
		"jti": str(uuid.uuid4()),
		"aud": "tableau",
		"sub": 'vendoradmin@aureusfg.com',
		"scp": ["tableau:views:embed", "tableau:metrics:embed"]
	},
		'9DuLGdhvcjC6Q++uyDsR6HZISohEPnqXrp6yvuw4334=',
		algorithm = "HS256",
		headers = {
		'kid': 'd56c3869-5df2-42da-a614-42206b0876c9',
		'iss': '3af22039-a099-4e37-8c57-f61f5e3344f8'
        }
    )
    return render_template("dashboard2.html",date=today,user=session["user"], jwt=token, version=msal.__version__)

@app.route("/dashboard3")
def dash3():
    token = jwt.encode(
	{
		"iss": '3af22039-a099-4e37-8c57-f61f5e3344f8',
		"exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=5),
		"jti": str(uuid.uuid4()),
		"aud": "tableau",
		"sub": 'vendoradmin@aureusfg.com',
		"scp": ["tableau:views:embed", "tableau:metrics:embed"]
	},
		'9DuLGdhvcjC6Q++uyDsR6HZISohEPnqXrp6yvuw4334=',
		algorithm = "HS256",
		headers = {
		'kid': 'd56c3869-5df2-42da-a614-42206b0876c9',
		'iss': '3af22039-a099-4e37-8c57-f61f5e3344f8'
        }
    )
    return render_template("dashboard3.html",date=today,user=session["user"], jwt=token, version=msal.__version__)

@app.route("/dashboard4")
def dash4():
    token = jwt.encode(
	{
		"iss": '3af22039-a099-4e37-8c57-f61f5e3344f8',
		"exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=5),
		"jti": str(uuid.uuid4()),
		"aud": "tableau",
		"sub": 'vendoradmin@aureusfg.com',
		"scp": ["tableau:views:embed", "tableau:metrics:embed"]
	},
		'9DuLGdhvcjC6Q++uyDsR6HZISohEPnqXrp6yvuw4334=',
		algorithm = "HS256",
		headers = {
		'kid': 'd56c3869-5df2-42da-a614-42206b0876c9',
		'iss': '3af22039-a099-4e37-8c57-f61f5e3344f8'
        }
    )
    return render_template("dashboard4.html",date=today,user=session["user"], jwt=token, version=msal.__version__)

@app.route("/dashboard5")
def dash5():
    token = jwt.encode(
	{
		"iss": '3af22039-a099-4e37-8c57-f61f5e3344f8',
		"exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=5),
		"jti": str(uuid.uuid4()),
		"aud": "tableau",
		"sub": 'vendoradmin@aureusfg.com',
		"scp": ["tableau:views:embed", "tableau:metrics:embed"]
	},
		'9DuLGdhvcjC6Q++uyDsR6HZISohEPnqXrp6yvuw4334=',
		algorithm = "HS256",
		headers = {
		'kid': 'd56c3869-5df2-42da-a614-42206b0876c9',
		'iss': '3af22039-a099-4e37-8c57-f61f5e3344f8'
        }
    )
    return render_template("dashboard5.html",date=today,user=session["user"], jwt=token, version=msal.__version__)

@app.route("/dashboard6")
def dash6():
    token = jwt.encode(
	{
		"iss": '3af22039-a099-4e37-8c57-f61f5e3344f8',
		"exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=5),
		"jti": str(uuid.uuid4()),
		"aud": "tableau",
		"sub": 'vendoradmin@aureusfg.com',
		"scp": ["tableau:views:embed", "tableau:metrics:embed"]
	},
		'9DuLGdhvcjC6Q++uyDsR6HZISohEPnqXrp6yvuw4334=',
		algorithm = "HS256",
		headers = {
		'kid': 'd56c3869-5df2-42da-a614-42206b0876c9',
		'iss': '3af22039-a099-4e37-8c57-f61f5e3344f8'
        }
    )
    return render_template("dashboard6.html",date=today,user=session["user"], jwt=token, version=msal.__version__)

@app.route("/dashboard7")
def dash7():
    token = jwt.encode(
	{
		"iss": '3af22039-a099-4e37-8c57-f61f5e3344f8',
		"exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=5),
		"jti": str(uuid.uuid4()),
		"aud": "tableau",
		"sub": 'vendoradmin@aureusfg.com',
		"scp": ["tableau:views:embed", "tableau:metrics:embed"]
	},
		'9DuLGdhvcjC6Q++uyDsR6HZISohEPnqXrp6yvuw4334=',
		algorithm = "HS256",
		headers = {
		'kid': 'd56c3869-5df2-42da-a614-42206b0876c9',
		'iss': '3af22039-a099-4e37-8c57-f61f5e3344f8'
        }
    )
    return render_template("dashboard7.html",date=today,user=session["user"], jwt=token, version=msal.__version__)

@app.route("/dashboard8")
def dash8():
    token = jwt.encode(
	{
		"iss": '3af22039-a099-4e37-8c57-f61f5e3344f8',
		"exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=5),
		"jti": str(uuid.uuid4()),
		"aud": "tableau",
		"sub": 'vendoradmin@aureusfg.com',
		"scp": ["tableau:views:embed", "tableau:metrics:embed"]
	},
		'9DuLGdhvcjC6Q++uyDsR6HZISohEPnqXrp6yvuw4334=',
		algorithm = "HS256",
		headers = {
		'kid': 'd56c3869-5df2-42da-a614-42206b0876c9',
		'iss': '3af22039-a099-4e37-8c57-f61f5e3344f8'
        }
    )
    return render_template("dashboard8.html",date=today,user=session["user"], jwt=token, version=msal.__version__)

@app.route("/dashboard9")
def dash9():
    token = jwt.encode(
	{
		"iss": '3af22039-a099-4e37-8c57-f61f5e3344f8',
		"exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=5),
		"jti": str(uuid.uuid4()),
		"aud": "tableau",
		"sub": 'vendoradmin@aureusfg.com',
		"scp": ["tableau:views:embed", "tableau:metrics:embed"]
	},
		'9DuLGdhvcjC6Q++uyDsR6HZISohEPnqXrp6yvuw4334=',
		algorithm = "HS256",
		headers = {
		'kid': 'd56c3869-5df2-42da-a614-42206b0876c9',
		'iss': '3af22039-a099-4e37-8c57-f61f5e3344f8'
        }
    )
    return render_template("dashboard9.html",date=today,user=session["user"], jwt=token, version=msal.__version__)

@app.route("/dashboard10")
def dash10():
    token = jwt.encode(
	{
		"iss": '3af22039-a099-4e37-8c57-f61f5e3344f8',
		"exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=5),
		"jti": str(uuid.uuid4()),
		"aud": "tableau",
		"sub": 'vendoradmin@aureusfg.com',
		"scp": ["tableau:views:embed", "tableau:metrics:embed"]
	},
		'9DuLGdhvcjC6Q++uyDsR6HZISohEPnqXrp6yvuw4334=',
		algorithm = "HS256",
		headers = {
		'kid': 'd56c3869-5df2-42da-a614-42206b0876c9',
		'iss': '3af22039-a099-4e37-8c57-f61f5e3344f8'
        }
    )
    return render_template("dashboard10.html",date=today,user=session["user"], jwt=token, version=msal.__version__)

@app.route("/dashboard11")
def dash11():
    token = jwt.encode(
	{
		"iss": '3af22039-a099-4e37-8c57-f61f5e3344f8',
		"exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=5),
		"jti": str(uuid.uuid4()),
		"aud": "tableau",
		"sub": 'vendoradmin@aureusfg.com',
		"scp": ["tableau:views:embed", "tableau:metrics:embed"]
	},
		'9DuLGdhvcjC6Q++uyDsR6HZISohEPnqXrp6yvuw4334=',
		algorithm = "HS256",
		headers = {
		'kid': 'd56c3869-5df2-42da-a614-42206b0876c9',
		'iss': '3af22039-a099-4e37-8c57-f61f5e3344f8'
        }
    )
    return render_template("dashboard11.html",date=today,user=session["user"], jwt=token, version=msal.__version__)

@app.route("/dashboard12")
def dash12():
    token = jwt.encode(
	{
		"iss": '3af22039-a099-4e37-8c57-f61f5e3344f8',
		"exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=5),
		"jti": str(uuid.uuid4()),
		"aud": "tableau",
		"sub": 'vendoradmin@aureusfg.com',
		"scp": ["tableau:views:embed", "tableau:metrics:embed"]
	},
		'9DuLGdhvcjC6Q++uyDsR6HZISohEPnqXrp6yvuw4334=',
		algorithm = "HS256",
		headers = {
		'kid': 'd56c3869-5df2-42da-a614-42206b0876c9',
		'iss': '3af22039-a099-4e37-8c57-f61f5e3344f8'
        }
    )
    return render_template("dashboard12.html",date=today,user=session["user"], jwt=token, version=msal.__version__)

@app.route("/dashboard13")
def dash13():
    token = jwt.encode(
	{
		"iss": '3af22039-a099-4e37-8c57-f61f5e3344f8',
		"exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=5),
		"jti": str(uuid.uuid4()),
		"aud": "tableau",
		"sub": 'vendoradmin@aureusfg.com',
		"scp": ["tableau:views:embed", "tableau:metrics:embed"]
	},
		'9DuLGdhvcjC6Q++uyDsR6HZISohEPnqXrp6yvuw4334=',
		algorithm = "HS256",
		headers = {
		'kid': 'd56c3869-5df2-42da-a614-42206b0876c9',
		'iss': '3af22039-a099-4e37-8c57-f61f5e3344f8'
        }
    )
    return render_template("dashboard13.html",date=today,user=session["user"], jwt=token, version=msal.__version__)

@app.route("/dashboard14")
def dash14():
    token = jwt.encode(
	{
		"iss": '3af22039-a099-4e37-8c57-f61f5e3344f8',
		"exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=5),
		"jti": str(uuid.uuid4()),
		"aud": "tableau",
		"sub": 'vendoradmin@aureusfg.com',
		"scp": ["tableau:views:embed", "tableau:metrics:embed"]
	},
		'9DuLGdhvcjC6Q++uyDsR6HZISohEPnqXrp6yvuw4334=',
		algorithm = "HS256",
		headers = {
		'kid': 'd56c3869-5df2-42da-a614-42206b0876c9',
		'iss': '3af22039-a099-4e37-8c57-f61f5e3344f8'
        }
    )
    return render_template("dashboard14.html",date=today,user=session["user"], jwt=token, version=msal.__version__)

@app.route("/dashboard15")
def dash15():
    token = jwt.encode(
	{
		"iss": '3af22039-a099-4e37-8c57-f61f5e3344f8',
		"exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=5),
		"jti": str(uuid.uuid4()),
		"aud": "tableau",
		"sub": 'vendoradmin@aureusfg.com',
		"scp": ["tableau:views:embed", "tableau:metrics:embed"]
	},
		'9DuLGdhvcjC6Q++uyDsR6HZISohEPnqXrp6yvuw4334=',
		algorithm = "HS256",
		headers = {
		'kid': 'd56c3869-5df2-42da-a614-42206b0876c9',
		'iss': '3af22039-a099-4e37-8c57-f61f5e3344f8'
        }
    )
    return render_template("dashboard15.html",date=today,user=session["user"], jwt=token, version=msal.__version__)

@app.route("/dashboard16")
def dash16():
    token = jwt.encode(
	{
		"iss": '3af22039-a099-4e37-8c57-f61f5e3344f8',
		"exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=5),
		"jti": str(uuid.uuid4()),
		"aud": "tableau",
		"sub": 'vendoradmin@aureusfg.com',
		"scp": ["tableau:views:embed", "tableau:metrics:embed"]
	},
		'9DuLGdhvcjC6Q++uyDsR6HZISohEPnqXrp6yvuw4334=',
		algorithm = "HS256",
		headers = {
		'kid': 'd56c3869-5df2-42da-a614-42206b0876c9',
		'iss': '3af22039-a099-4e37-8c57-f61f5e3344f8'
        }
    )
    return render_template("dashboard16.html",date=today,user=session["user"], jwt=token, version=msal.__version__)

@app.route("/login")
def login():
    # Technically we could use empty list [] as scopes to do just sign in,
    # here we choose to also collect end user consent upfront
    session["flow"] = _build_auth_code_flow(scopes=app_config.SCOPE)
    return render_template("login.html", auth_url=session["flow"]["auth_uri"], version=msal.__version__)

@app.route(app_config.REDIRECT_PATH)  # Its absolute URL must match your app's redirect_uri set in AAD
def authorized():
    try:
        cache = _load_cache()
        result = _build_msal_app(cache=cache).acquire_token_by_auth_code_flow(
            session.get("flow", {}), request.args)
        if "error" in result:
            return render_template("auth_error.html", result=result)
        session["user"] = result.get("id_token_claims")
        _save_cache(cache)
    except ValueError:  # Usually caused by CSRF
        pass  # Simply ignore them
    return redirect(url_for("index"))

@app.route("/logout")
def logout():
    session.clear()  # Wipe out user and its token cache from session
    return redirect(  # Also logout from your tenant's web session
        app_config.AUTHORITY + "/oauth2/v2.0/logout" +
        "?post_logout_redirect_uri=" + url_for("index", _external=True))

@app.route("/graphcall")
def graphcall():
    token = _get_token_from_cache(app_config.SCOPE)
    if not token:
        return redirect(url_for("login"))
    graph_data = requests.get(  # Use token to call downstream service
        app_config.ENDPOINT,
        headers={'Authorization': 'Bearer ' + token['access_token']},
        ).json()
    return render_template('display.html', result=graph_data)


def _load_cache():
    cache = msal.SerializableTokenCache()
    if session.get("token_cache"):
        cache.deserialize(session["token_cache"])
    return cache

def _save_cache(cache):
    if cache.has_state_changed:
        session["token_cache"] = cache.serialize()

def _build_msal_app(cache=None, authority=None):
    return msal.ConfidentialClientApplication(
        app_config.CLIENT_ID, authority=authority or app_config.AUTHORITY,
        client_credential=app_config.CLIENT_SECRET, token_cache=cache)

def _build_auth_code_flow(authority=None, scopes=None):
    return _build_msal_app(authority=authority).initiate_auth_code_flow(
        scopes or [],
        redirect_uri=url_for("authorized", _external=True))

def _get_token_from_cache(scope=None):
    cache = _load_cache()  # This web app maintains one cache per session
    cca = _build_msal_app(cache=cache)
    accounts = cca.get_accounts()
    if accounts:  # So all account(s) belong to the current signed-in user
        result = cca.acquire_token_silent(scope, account=accounts[0])
        _save_cache(cache)
        return result

app.jinja_env.globals.update(_build_auth_code_flow=_build_auth_code_flow)  # Used in template

if __name__ == "__main__":
    app.run()

