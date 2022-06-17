# Predicción de la Copa América de fútbol 2021 con Aprendizaje Automático⚽🏆

Proyecto realizado para la asignatura de Machine Learning (ML), el cual consistió en buscar un proyecto de ML ya implementado, para así investigar la técnica aplicada, y posteriormente adaptar el modelo a un problema real diferente, modificando los aspectos necesarios para su implementación.


## Proyecto Base💻

El proyecto utilizado como base para la implementación se titula, [_Soccer World Cup 2018 Winner_](https://www.kaggle.com/code/agostontorok/soccer-world-cup-2018-winner/notebook) y fue desarrollado por [Agoston Torok](https://www.kaggle.com/agostontorok).


## Implementación del Modelo📋

Para poder adaptar el proyecto base a la predicción de la Copa América, se tuvo que crear un conjunto de datos del torneo ([Dataset Copa America](https://github.com/felipeee-mg/Prediccion_CopaAmerica2021/blob/main/datasets/Copa_America_Dataset.csv)), y así adicionarlo a los dos conjuntos de datos ya establecidos en el proyecto base ([FIFA Soccer Rankings](https://www.kaggle.com/datasets/tadhgfitzgerald/fifa-international-soccer-mens-ranking-1993now) y [International football results from 1872 to 2021](https://www.kaggle.com/datasets/martj42/international-football-results-from-1872-to-2017)).

En cuanto a la implementación del modelo de predicción, se utilizó la técnica de Regresión Logística para el entrenamiento de los conjuntos de datos y la posterior predicción de los partidos.

Se puede ver todo el proceso de implantación en el archivo .ipynb disponible en el repositorio ([Modelo Copa America](https://github.com/felipeee-mg/Prediccion_CopaAmerica2021/blob/main/modelo_copa_america.ipynb)).


## Aplicación Web 🚀

Se implementó el proyecto de aprendizaje automático en una aplicación web con la ayuda del framework Flask, para que así el usuario pueda interactuar con el modelo y probar la calidad de la solución. Esta aplicación se encuentra disponible en el siguiente link: [Predicción Copa América 2021](https://prediccion-copa-america-2021.herokuapp.com/)


## Tecnologías Utilizadas 🛠
 * Python - Para la implementación del modelo de aprendizaje automático, en conjunto con las librerías: pandas, Matplotlib, Sklearn y Joblib.
 * Flask - Para la aplicación web.
 * HTML y CSS - Para la estructura y estilos de la aplicación.
 * Heroku - Para el deploy de la aplicación web.
