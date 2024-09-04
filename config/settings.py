from environs import Env

env = Env()
env.read_env()  # read .env file, if it exists

# email related settings
with env.prefixed("EMAIL_"):
    EMAIL_SENDER = env.str("SENDER")
    EMAIL_RECEIVER = env.str("RECEIVER")
    EMAIL_PASSWORD = env.str("PASSWORD")
    EMAIL_HOST = env.str("HOST")
    EMAIL_PORT = env.int("PORT")