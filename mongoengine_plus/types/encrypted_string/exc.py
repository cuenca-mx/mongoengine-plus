class NoDataKeyFound(Exception):
    """
    No se encontró un data_key en la BD de Mongo
    Por lo que no se puede encriptar o desencriptar
    algún dato
    """
