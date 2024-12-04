import pandas as pd
import hashlib

# Cargar o crear archivo CSV de usuarios
def load_users():
    try:
        return pd.read_csv("users.csv")
    except FileNotFoundError:
        # Crear un archivo vacío si no existe
        df = pd.DataFrame(columns=["username", "password"])
        df.to_csv("users.csv", index=False)
        return df

# Guardar usuario en el archivo CSV
def save_user(username, password_hash):
    users = load_users()
    new_user = pd.DataFrame({"username": [username], "password": [password_hash]})
    users = pd.concat([users, new_user], ignore_index=True)
    users.to_csv("users.csv", index=False)

# Encriptar contraseñas
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Autenticar usuario
def authenticate_user(username, password):
    users = load_users()
    password_hash = hash_password(password)
    return not users[(users['username'] == username) & (users['password'] == password_hash)].empty

# Verificar si el usuario ya existe
def user_exists(username):
    users = load_users()
    return username in users['username'].values
