from flask import Flask, render_template, request
import pandas as pd
from joblib import load
import numpy as np

with open(f'model/modelo_copa_america.joblib','rb') as f:
    model = load(f)

app = Flask(__name__)

@app.route("/")
def inicio():
    return render_template("inicio.html")

@app.route("/prediccion_copa_america")
def prediccion_copa_america():

    rankings = pd.read_csv('datasets/fifa_ranking.csv')
    copa_america = pd.read_csv('datasets/Copa_America_Dataset.csv')

    rankings = rankings.loc[:,['rank', 'country_full', 'country_abrv', 'cur_year_avg_weighted', 'rank_date', 
                           'two_year_ago_weighted', 'three_year_ago_weighted']]
    rankings['weighted_points'] =  rankings['cur_year_avg_weighted'] + rankings['two_year_ago_weighted'] + rankings['three_year_ago_weighted']
    rankings['rank_date'] = pd.to_datetime(rankings['rank_date'])

    copa_america = copa_america.dropna(how='all')
    copa_america = copa_america.set_index('Team')

    rankings = rankings.set_index(['rank_date'])\
            .groupby(['country_full'], group_keys=False)\
            .resample('D').first()\
            .fillna(method='ffill')\
            .reset_index()

    margin = 0.05

    copa_america_rankings = rankings.loc[(rankings['rank_date'] == rankings['rank_date'].max()) & rankings['country_full'].isin(copa_america.index.unique())]
    copa_america_rankings = copa_america_rankings.set_index(['country_full'])

    from itertools import combinations

    copa_america['points'] = 0
    copa_america['total_prob'] = 0
    resultados_grupo_a = []
    resultados_grupo_b = []

    for group in set(copa_america['Group']):
        for home, away in combinations(copa_america.query('Group == "{}"'.format(group)).index, 2):
            partido = ("{} vs. {}: ".format(home, away))
            row = pd.DataFrame(np.array([[np.nan, np.nan, np.nan, True]]), columns=['average_rank', 'rank_difference', 'point_difference','is_stake'])
            home_rank = copa_america_rankings.loc[home, 'rank']
            home_points = copa_america_rankings.loc[home, 'weighted_points']
            opp_rank = copa_america_rankings.loc[away, 'rank']
            opp_points = copa_america_rankings.loc[away, 'weighted_points']
            row['average_rank'] = (home_rank + opp_rank) / 2
            row['rank_difference'] = home_rank - opp_rank
            row['point_difference'] = home_points - opp_points
        
            home_win_prob = model.predict_proba(row)[:,1][0]
            copa_america.loc[home, 'total_prob'] += home_win_prob
            copa_america.loc[away, 'total_prob'] += 1-home_win_prob

            points = 0
            if home_win_prob <= 0.5 - margin:
                resultado = ("{} gana con una probabilidad de {:.2f}".format(away, 1-home_win_prob))
                if group == "A":
                    resultados_grupo_a.append((partido + resultado))
                else:
                    resultados_grupo_b.append((partido + resultado))
                copa_america.loc[away, 'points'] += 3
            if home_win_prob > 0.5 - margin:
                points = 1
            if home_win_prob >= 0.5 + margin:
                points = 3
                copa_america.loc[home, 'points'] += 3
                resultado = ("{} gana con una probabilidad de {:.2f}".format(home, home_win_prob))
                if group == "A":
                    resultados_grupo_a.append((partido + resultado))
                else:
                    resultados_grupo_b.append((partido + resultado))
            if points == 1:
                resultado = ("Empate")
                if group == "A":
                    resultados_grupo_a.append((partido + resultado))
                else:
                    resultados_grupo_b.append((partido + resultado))
                copa_america.loc[home, 'points'] += 1
                copa_america.loc[away, 'points'] += 1


    pairing = [0,7,1,6,3,4,2,5]
    copa_america = copa_america.sort_values(by=['Group', 'points', 'total_prob'], ascending=False).reset_index()
    next_round_copa_america = copa_america.groupby('Group').nth([0, 1, 2, 3])
    next_round_copa_america = next_round_copa_america.reset_index()
    next_round_copa_america = next_round_copa_america.loc[pairing]
    next_round_copa_america = next_round_copa_america.set_index('Team')

    resultados_cuartos = []
    resultados_semi = []
    resultados_final = []

    finals = ['quarterfinal', 'semifinal', 'final']

    for f in finals:
        iterations = int(len(next_round_copa_america) / 2)
        winners = []

        for i in range(iterations):
            home = next_round_copa_america.index[i*2]
            away = next_round_copa_america.index[i*2+1]
            partido = ("{} vs. {}: ".format(home, away))
            row = pd.DataFrame(np.array([[np.nan, np.nan, np.nan, True]]), columns=['average_rank', 'rank_difference', 'point_difference','is_stake'])
            home_rank = copa_america_rankings.loc[home, 'rank']
            home_points = copa_america_rankings.loc[home, 'weighted_points']
            opp_rank = copa_america_rankings.loc[away, 'rank']
            opp_points = copa_america_rankings.loc[away, 'weighted_points']
            row['average_rank'] = (home_rank + opp_rank) / 2
            row['rank_difference'] = home_rank - opp_rank
            row['point_difference'] = home_points - opp_points

            home_win_prob = model.predict_proba(row)[:,1][0]
            if model.predict_proba(row)[:,1] <= 0.5:
                resultado = ("{} gana con una probabilidad de {:.2f}".format(away, 1-home_win_prob))
                winners.append(away)
                if f == "quarterfinal":
                    resultados_cuartos.append((partido + resultado))
                elif f == "semifinal":
                    resultados_semi.append((partido + resultado))
                elif f == "final":
                    resultados_final.append((partido + resultado))
            else:
                resultado = ("{} gana con una probabilidad de {:.2f}".format(home, home_win_prob))
                if f == "quarterfinal":
                    resultados_cuartos.append((partido + resultado))
                elif f == "semifinal":
                    resultados_semi.append((partido + resultado))
                elif f == "final":
                    resultados_final.append((partido + resultado))
                winners.append(home)

        next_round_copa_america = next_round_copa_america.loc[winners]

    return render_template("prediccion_copa_america.html", resultados_grupo_a=resultados_grupo_a, resultados_grupo_b=resultados_grupo_b, resultados_cuartos=resultados_cuartos, resultados_semi=resultados_semi, resultados_final=resultados_final)



@app.route("/prediccion_partido", methods=["POST","GET"])
def prediccion_partido():

    rankings = pd.read_csv('datasets/fifa_ranking.csv')
    copa_america = pd.read_csv('datasets/Copa_America_Dataset.csv')

    rankings = rankings.loc[:,['rank', 'country_full', 'country_abrv', 'cur_year_avg_weighted', 'rank_date', 
                           'two_year_ago_weighted', 'three_year_ago_weighted']]
    rankings['weighted_points'] =  rankings['cur_year_avg_weighted'] + rankings['two_year_ago_weighted'] + rankings['three_year_ago_weighted']
    rankings['rank_date'] = pd.to_datetime(rankings['rank_date'])

    copa_america = copa_america.dropna(how='all')
    copa_america = copa_america.set_index('Team')

    rankings = rankings.set_index(['rank_date'])\
            .groupby(['country_full'], group_keys=False)\
            .resample('D').first()\
            .fillna(method='ffill')\
            .reset_index()

    margin = 0.05

    copa_america_rankings = rankings.loc[(rankings['rank_date'] == rankings['rank_date'].max()) & rankings['country_full'].isin(copa_america.index.unique())]
    copa_america_rankings = copa_america_rankings.set_index(['country_full'])

    if request.method == "GET":
        return render_template("prediccion_partido.html")

    if request.method == "POST":

        home = request.form['local']
        away = request.form['visita']

        partido = ("{} vs. {}: ".format(home, away))
        row = pd.DataFrame(np.array([[np.nan, np.nan, np.nan, True]]), columns=['average_rank', 'rank_difference', 'point_difference','is_stake'])
        home_rank = copa_america_rankings.loc[home, 'rank']
        home_points = copa_america_rankings.loc[home, 'weighted_points']
        opp_rank = copa_america_rankings.loc[away, 'rank']
        opp_points = copa_america_rankings.loc[away, 'weighted_points']
        row['average_rank'] = (home_rank + opp_rank) / 2
        row['rank_difference'] = home_rank - opp_rank
        row['point_difference'] = home_points - opp_points
        
        home_win_prob = model.predict_proba(row)[:,1][0]


        points = 0
        if home_win_prob <= 0.5 - margin:
            resultado = ("{} gana con una probabilidad de {:.2f}".format(away, 1-home_win_prob))
            resultado_partido = (partido + resultado)
        if home_win_prob > 0.5 - margin:
            points = 1
        if home_win_prob >= 0.5 + margin:
            points = 3
            resultado = ("{} gana con una probabilidad de {:.2f}".format(home, home_win_prob))
            resultado_partido = (partido + resultado)
        if points == 1:
            resultado = ("Empate")
            resultado_partido = (partido + resultado)

        return render_template("prediccion_partido.html", resultado_partido=resultado_partido)

if __name__ == "__main__":
    app.run(debug=True)