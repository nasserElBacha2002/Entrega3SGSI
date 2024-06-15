import os
from pymongo import MongoClient, errors
import logging

# Configuración del log
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    handlers=[logging.FileHandler("security.log"),
                              logging.StreamHandler()])

def connect_db():
    """
    Establece la conexión con la base de datos MongoDB.
    """
    try:
        # Conexión a la base de datos utilizando la URL proporcionada
        mongo_url = os.getenv('MONGODB_URL')
        client = MongoClient(mongo_url)
        db = client['Entrega3']
        logging.info("Conexión a la base de datos MongoDB exitosa")
        return db
    except errors.ConnectionFailure as e:
        # Manejo de errores en la conexión
        logging.error(f"Error en la conexión a la base de datos MongoDB: {e}")
        return None

def create_collection(db):
    """
    Crea la colección 'users' en la base de datos si no existe.
    """
    try:
        collection = db['users']
        logging.info("Colección creada exitosamente")
        return collection
    except errors.PyMongoError as e:
        # Manejo de errores al crear la colección
        logging.error(f"Error al crear la colección: {e}")

def is_valid_input(input_str):
    """
    Verifica si la entrada no contiene caracteres maliciosos.
    """
    if isinstance(input_str, str) and '$' not in input_str and '>' not in input_str:
        return True
    return False

def add_user(collection, username, password):
    """
    Añade un nuevo usuario a la colección 'users' utilizando entradas sanitizadas.
    """
    if is_valid_input(username) and is_valid_input(password):
        try:
            # Inserción de documento con sanitización de entrada
            collection.insert_one({'username': username, 'password': password})
            logging.info(f"Usuario {username} añadido exitosamente")
        except errors.PyMongoError as e:
            # Manejo de errores al añadir usuario
            logging.error(f"Error al añadir usuario: {e}")
    else:
        logging.warning(f"Intento de inyección de código detectado: {username}, {password}")

def main():
    """
    Función principal que ejecuta el flujo de conexión, creación de colección y 
    adición de usuarios incluyendo un caso de prueba de inyección de código.
    """
    db = connect_db()  # Conexión a la base de datos
    if db is not None:  # Verifica explícitamente si db no es None
        collection = create_collection(db)  # Creación de la colección
        if collection is not None:  # Verifica explícitamente si collection no es None
            # Añadir usuarios de prueba
            add_user(collection, 'admin', 'securepassword')
            add_user(collection, 'user1', 'anotherpassword')

            # Caso de prueba: intento de inyección de código
            malicious_input = {'$gt': ''}
            try:
                add_user(collection, 'intruder', malicious_input)
            except errors.PyMongoError as e:
                logging.error(f"Intento de inyección de código detectado: {e}")

if __name__ == "__main__":
    main()
