import warnings
warnings.filterwarnings("ignore", category=FutureWarning)
from flask import render_template, Flask,abort
import logging
import db


APP = Flask(__name__)

@APP.route('/')
def index():
   return render_template('index.html')
@APP.route('/stats/')    
def stats():
    stats=db.execute('''
      select
        (select count(*) from CATEGORIA) as nr_categories,
        (select count(*) from CEREMONIA) as nr_cerimonies,
        (select count(*) from FILME) as nr_films,
        (select count(*) from NOMEACAO) as nr_nominations,
        (select count(*) from NOMEADO) as nr_nominees
      ''').fetchone()
    logging.info(stats)
    return render_template('stats.html',stats=stats)


@APP.route('/ceremony/')
def list_ceremony():
    Cerimonia = db.execute('''
      SELECT Num_Cerimonia, Ano
      From CERIMONIA
      ORDER BY Num_Cerimonia
    ''').fetchall()
    return render_template('ceremony-list.html', Cerimonia=Cerimonia)

@APP.route('/ceremony/<int:cn>/')
def view_year_by_ceremony(cn):
    ceremony = db.execute('''
      SELECT Num_Cerimonia,Ano
      From CERIMONIA
      WHERE Num_Cerimonia=?
    ''',[cn]).fetchone()
    if ceremony is None:
        abort(404,'Num_Cerimonia {} does not exist.'.format(cn))

    categories = db.execute('''
        SELECT DISTINCT Categoria_Canonica
        FROM Nomeacao
        WHERE Num_Cerimonia = ?
        ORDER BY Categoria_Canonica
    ''', [cn]).fetchall()   

    nominations = db.execute('''
    SELECT 
        IDNomeacao,
        Categoria_Canonica,
        IDNomeado,
        Nome,
        Titulo,
        Vencedor,
        FROM NOMEACAO NATURAL JOIN NOMEIAN NATURAL JOIN NOMEADO NATURAL JOIN FILME
        WHERE Num_Cerimonia = ?
        ORDER BY Categoria_Canonica
                ''', [cn]).fetchall()   

    return render_template('ceremony.html', Cerimonia=ceremony,Categoria=categories,Nomeacao=nominations)

@APP.route('/ceremony/search/<path:year>/')
def search_ceremony(year):
   ceremonies = db.execute('''
     SELECT Num_Cerimonia ,Ano
     FROM CERIMONIA
     WHERE Ano= ?
   ''',[year]).fetchall()

   return render_template('ceremony-search.html', Ano=year, Cerimonia=ceremonies)



@APP.route('/film/')
def list_film():
    films= db.execute('''
      SELECT IDFilme, Titulo
      From FILME
      ORDER BY IDFilme
    ''').fetchall()
    return render_template('film-list.html', films=films)

@APP.route('/film/<id>/')
def get_film(id):
    film = db.execute(
      '''
      SELECT IDFilme, Titulo
      FROM FILME
      WHERE IDFilme = ?
      ''', [id]).fetchone()

    if film is None:
        abort(404, f"IDFilme {id} does not exist.")

    nominations = db.execute(
        '''
        SELECT 
            IDNomeacao,
            Categoria_Canonica,
            Nome,
            Vencedor
        FROM NOMEACAO NATURAL JOIN NOMEIAN NATURAL JOIN NOMEADO
        WHERE IDFilme = ?
        ORDER BY Categoria_Canonica
        ''', [id]
    ).fetchall()

    return render_template('film.html', Filme=film, Nomeacao=nominations)


@APP.route('/film/search/<txt>/')
def search_film(txt):
  like_txt = '%' + txt + '%'
  films = db.execute(
      ''' 
      SELECT IDFilme, Titulo
      FROM FILME
      WHERE Titulo LIKE ?
      ''', [like_txt]).fetchall()
  return render_template('film-search.html',
           txt=txt,Filme=films)


@APP.route('/nominee/')
def list_nominee():
    nominees = db.execute('''
        SELECT IDNomeado, Nome
        FROM NOMEADO
        ORDER BY IDNomeado
    ''').fetchall()

    return render_template('nominee-list.html', Nomeado=nominees)


@APP.route('/nominee/<id>/')
def get_nominee(id):
    nominee= db.execute(
      '''
      SELECT IDNomedo, Nome
      FROM NOMEADO
      WHERE IDNomeado = ?
      ''', [id]).fetchone()

    if id is None:
     abort(404, 'IDNomeado {} does not exist.'.format(id))
    
    nominations=db.execute('''SELECT 
        IDNomeacao,
        Vencedor,
        Detalhes,
        Citacao,
        Notas,
        Num_Cerimonia,
        Categoria_Canonica,
        IDFilme,
        FROM NOMEACAO
        WHERE IDNomeacao = ?
        ORDER BY Num_Cerimonia
      ''',
      [id]
    ).fetchall()
    return render_template('nominee.html', Nome=nominee,Nomeacao=nominations)

@APP.route('/nominee/search/<txt>/')
def search_nominee(txt):
  like_txt = '%' + txt + '%'
  nominees = db.execute(
      ''' 
      SELECT IDNomeado, Nome
      FROM NOMEADO
      WHERE Nome LIKE ?
      ''', [like_txt]).fetchall()
  return render_template('nominee-search.html',
           txt=txt,Nome=nominees)

@APP.route('/nomination/')
def list_nomination():
    nomination = db.execute('''
        SELECT 
        IDNomeacao,
        Num_Cerimonia,
        IDFilme,
        Categoria_Canonica,
        NOMEADO.Nome,
        Vencedor,
        FROM Nomeacao NATURAL JOIN NOMEIAN NATURAL JOIN NOMEADO
        ORDER BY IDNomeacao
    ''').fetchall()

    return render_template('nomination-list.html', nomination=nomination)


@APP.route('/nomination/<id>/')
def get_nomination(id):
    nomination = db.execute(
        '''
        SELECT 
        Nomeacao.ID,
        Nomeacao.Num_Cerimonia,
        Nomeacao.IDFilme,
        Nomeacao.Categoria_Canonica,
        Nomeacao.IDNomeado,
        NOMEADO.Nome,
        Nomeacao.Vencedor,
        Nomeacao.Detalhes,
        Nomeacao.Notas,
        Nomeacao.Citacao
        FROM Nomeacao NATURAL JOIN  NOMEIAN NATURAL JOIN NOMEADO
        WHERE IDNomeacao = ?
        ''', 
        [id]
    ).fetchone()

    if nomination is None:
        abort(404, f'NominatioIDNomeado {id} does not exist.')

    return render_template('nomination.html', nomination=nomination)

@APP.route('/category/') 
def list_category(): 
    Category = db.execute(''' 
            SELECT Categoria_Canonica,Classe 
            From CATEGORIA 
            ORDER BY Categoria_Canonica 
            ''').fetchall()
    return render_template('categoria_list.html', Categoria=Category)

