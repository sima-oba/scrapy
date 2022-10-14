import glob
import json
import logging
import os
import shutil
import geopandas
import patoolib
import requests
from geopandas import GeoDataFrame
from shapely.geometry import mapping

from .. import publisher

log = logging.getLogger(__name__)


def _extract_shp(url: str, folder: str) -> GeoDataFrame:
    '''function to extract a compressed "shp" file'''
    zip_file = folder + ".zip"

    log.debug('Downloading from: ' + url)
    log.debug('Downloading data: ' + zip_file)
    r = requests.get(url, allow_redirects=True)

    if r.status_code == 200:
        with open(zip_file, 'wb') as file:
            file.write(r.content)

        if os.path.exists(folder) is False:
            os.mkdir(folder)

        log.debug('Extracting file: ' + zip_file)
        patoolib.extract_archive(zip_file, outdir=folder)
        files = glob.glob(folder + "/*.shp")

        log.debug('Shapefile found: ' + str(files))
        df = geopandas.read_file(files[0])

        os.remove(zip_file)
        shutil.rmtree(folder)
    else:
        raise logging.exception(f"Download error with status code: {r.status_code}")

    return df


def hydrography_vectors(url):
    df = _extract_shp(url, '/tmp/hidrografia_ana')
    publisher.publish('HYDROGRAPHY_ANA', df)


def limit_n1(url):
    folder = '/tmp/limit_n1'
    file = folder + '.gpkg'

    log.debug('Baixando dados: ' + file)
    r = requests.get(url, allow_redirects=True)
    open(file, 'wb').write(r.content)

    log.debug('Shapefile encontrado: ' + str(file))
    df = geopandas.read_file(file)
    os.remove(file)

    for row in df.iterrows():
        data = row[1].to_dict()
        data['geometry'] = mapping(data['geometry'])
        publisher.publish('LIMIT_LVL_1', data)


def limit_n2(url):
    df = _extract_shp(url, '/tmp/limite_n2')
    publisher.publish('LIMIT_LVL_2', df)


def limit_n4(url):
    df = _extract_shp(url, '/tmp/bacia_rio_grande')
    publisher.publish('BASIN_RIO_GRANDE', df)


def limit_n5(url):
    df = _extract_shp(url, '/tmp/area_de_contribuicao_nivel_5')

    for row in df.iterrows():
        data = row[1].to_dict()
        data['geometry'] = mapping(data['geometry'])
        publisher.publish('CONTRIB', data)


def qmld_flow(url):
    df = _extract_shp(url, '/tmp/vazao_especifica_qmlb')
    publisher.publish('FLOW_RATE', df)


def q90_flow(url):
    df = _extract_shp(url, '/tmp/vazao_especifica_q90')
    publisher.publish('FLOW_RATE', df)


def water_availability(url):
    df = _extract_shp(url, '/tmp/disponibilidade_hidrica')

    for row in df.iterrows():
        data = row[1].to_dict()
        data['geometry'] = mapping(data['geometry'])
        # publisher.publish('WATER_AVAILABILITY', data)

    log.debug(df.size + ' regs found')
    

def water_safety_index(url):
    df = _extract_shp(url, '/tmp/indice_seguranca_hidrica')

    for row in df.iterrows():
        row = row[1].to_dict()
        data = {
            'brazil': row['brasil'],
            'co_basin': row['cobacia'],
            'economical': row['economica'],
            'ecosystem': row['ecossistem'],
            'human': row['humana'],
            'resilience': row['resilienc'],
            'area': row['Shape_Area'],
            'length': row['Shape_Leng'],
            'geometry': mapping(row['geometry'])
        }
        publisher.publish('WATER_SECURITY', data)


def water_bodies(url):
    folder = 'corpos_hidricos'
    zipFile = folder + '.zip'

    log.debug('Downloading data: ' + zipFile)
    r = requests.get(url, allow_redirects=True)
    open(zipFile, 'wb').write(r.content)

    if os.path.exists(folder) is False:
        os.mkdir(folder)

    log.debug('Extracting file: ' + zipFile)
    patoolib.extract_archive(zipFile, outdir=folder)
    files = glob.glob(folder + '/Gdba_lito/Hidrografia/*bifilar.shp')

    log.debug('Shapefile found: ' + str(files))
    df = geopandas.read_file(files[0])

    os.remove(zipFile)
    shutil.rmtree(folder)

    for row in df.iterrows():
        row = row[1].to_dict()
        data = {
            'type': row['TIPO'],
            'name': row['NOME'],
            'geometry': mapping(row['geometry'])
        }
        publisher.publish('WATERBODY', data)


def sao_francisco_micro_basins(url):
    df = _extract_shp(url, '/tmp/micro_bacias')
    publisher.publish('BASIN', df)


def sao_francisco_basin(url):
    df = _extract_shp(url, '/tmp/bacia_sao_francisco')
    publisher.publish('BASIN', df)


def aquifer(url):
    dataframe = _extract_shp(url, '/tmp/aquifero')

    for row in dataframe.iterrows():
        row = row[1].to_dict()
        data = {
            'imported_id': str(row['OBJECTID']),
            'type': row['SAA_NM_SIS'],
            'name': row['SAA_NM_AQU'],
            'area': row['SHAPE_AREA'],
            'length': row['SHAPE_LEN'],
            'geometry': mapping(row['geometry'])
        }
        publisher.publish('AQUIFER', data)


def irrigated_areas(url):
    folder = 'areas_irrigadas'
    labels = ['fid', 'Shape_Leng', 'Shape_Area', 'geometry']
    dataframe = _extract_shp(url, folder)
    dic = dataframe.to_dict()

    for t in range(len(dataframe)):
        reg = json.loads(json.dumps({
            'imported_id':  str(dic[labels[0]][t]),
            'length':       dic[labels[1]][t],
            'area':         dic[labels[2]][t],
            'geometry':     mapping(dic[labels[3]][t])
        }))
        publisher.publish('IRRIGATED_AREA', reg)


def center_pivots(url):
    df = _extract_shp(url, '/tmp/pivot')

    for row in df.iterrows():
        data = row[1].to_dict()
        data['area'] = data.pop('AREAHA')
        data['geometry'] = mapping(data['geometry'])

        publisher.publish('PIVOT', data)

def carinhanha_basin(url):
    df = _extract_shp(url, '/tmp/carinhanha')

    for row in df.iterrows():
        data = row[1].to_dict()
        data['geometry'] = mapping(data['geometry'])

        #TODO: nome do tópico
        publisher.publish("CARINHANHA_BASIN", data)

def corrente_basin(url):
    df = _extract_shp(url, '/tmp/corrente')

    for row in df.iterrows():
        data = row[1].to_dict()
        data['geometry'] = mapping(data['geometry'])

        #TODO: nome do tópico
        publisher.publish('CORRENTE_BASIN', data)

