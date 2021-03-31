from flask import Flask ,render_template , redirect , request
import pandas as pd
import nlp_v3 as nl
import json
import plotly.express as px


app = Flask(__name__)
app.jinja_env.add_extension('jinja2.ext.loopcontrols')
dataset=pd.read_csv ("Scrap_Assurances.csv")

#gets the disctinct names of agencies

nom=[]
for i in range(dataset.shape[0]):
	if(dataset["assurance"][i] not in nom and dataset["assurance"][i] not in ['avocotes.com','assurland.com','assuranoo.re','elly-assurance.fr','leblogpatrimoine.com','lecomparateurassurance.com','lelynx.fr','miel-paris.com','mutac.com','objectif-taux.fr','réassurez-moi.fr','storeonline.fr']
):
		nom.append(dataset["assurance"][i])

# Get a list of the rates and years for an insurance name
def get_rate_year (nom_assurance):
	rate=[]
	year=[]
	for i in range(dataset.shape[0]):
		if(dataset["assurance"][i] ==nom_assurance ):
			rate.append(dataset["note"][i])
			year.append(dataset["date"][i])
	return rate,year

# Get the average rate for a choosen year
def avg_per_year(y,r,year):
	somme=0
	nb=0
	for i in range(len(year)):
		if(y==year[i][len(year[i])-4:len(year[i])] ):
			somme=somme+int(r[i])
			nb=nb+1
	return(somme/nb)

# It gets the unique list of years
def get_distinct_year(y):
	year=[]
	for i in range(len(y)):
		if(len(y[i])<=10):
			if(y[i][len(y[i])-4:len(y[i])] not in year):
				year.append(y[i][len(y[i])-4:len(y[i])])
	return year


# Generate an interactive html graph of the average rates per year
def generate_html_graph(n):
	r,y=get_rate_year(n)
	year=get_distinct_year(y)
	list_rates=[]
	for i in  range(len(year)):
		list_rates.append(avg_per_year(year[i],r,y))
	year=year[::-1]
	list_rates=list_rates[::-1]
	df=pd.DataFrame({"year":year ,"rate":list_rates})
	fig = px.line(df,x="year", y="rate",hover_name="rate", render_mode="svg")
	fig.write_html("./Templates/graph/"+n+".html")

# Returns a list of all informations which its comments contains a given word
def verif_exist_comment(dataset,x):
    k=dataset["commentaire"]
    liste=[]
    id=0
    for i in range(len(k)):
        if (str(k[i]).find(x)!=-1):
           id=id+1
           liste.append([id,dataset["nom"].iloc[i],dataset["date"].iloc[i],dataset["commentaire"].iloc[i],dataset["note"].iloc[i]])
    return liste


# It assembles all the data that corresponds to the 10 highest words frequency 
def create_data(frequency_words):
	data=[]
	for i in range(20):
		list_comments=verif_exist_comment(dataset,frequency_words[i])
		data.append([frequency_words[i],list_comments])

	return data





# Creating global variables for lda route

prefix="ldavis_prepared_"
extension=".html"


words_to_remove=["très","j'ai","plus","toujours","toutes","questions","d'assurance","dossier","avoir","l'assurance","tres"]
@app.route('/assurance',methods=["POST"])
def index():
	 select = request.form.get('nom')
	 nl.LDA(dataset,select)
	 nom_html=prefix+str(select)+extension
	 nl.wordcloud(str(select),dataset)
	 src="wc_"+select+".png"
	 generate_html_graph(select)
	 graph_name=select+".html"
	 return render_template('dashboard.html',nom=nom,nom_html=nom_html,selected=select,src=src,graph=graph_name)


@app.route('/',methods=["GET" , "POST"])
def index2():
	nl.LDA(dataset,"zen-up.com")
	nom_html_zen=prefix+"zen-up.com"+extension
	generate_html_graph("zen-up.com")
	nl.wordcloud("zen-up.com",dataset)
	return render_template('dashboard.html',nom=nom,nom_html=nom_html_zen,selected="zen-up.com",src="wc_zen-up.com.png",graph="zen-up.com.html")



@app.route('/comments.html',methods=["POST"])
def index3():
	select = request.form.get('nom_com')
	list_word_freq=nl.frequencies(str(select),dataset,words_to_remove)
	data=create_data(list_word_freq)
	return render_template('comments.html',nom=nom,data=data,selected=select)

@app.route('/comments',methods=["GET" , "POST"])
def index4():
	list_word_freq=nl.frequencies("zen-up.com",dataset,words_to_remove)
	data=create_data(list_word_freq)
	return render_template('comments.html',nom=nom,data=data,selected="zen-up.com")


if __name__ == "__main__":
	app.run(host="127.0.0.1", port=5000 , debug=True)