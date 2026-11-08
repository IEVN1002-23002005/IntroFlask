class DevelopmentConfig():
    DEBUG=True
    MYSQL_HOST='localhost'
    MYSQL_PORT=3306
    MYSQL_USER='edo'
    MYSQL_PASSWORD='root'
    MYSQL_DB='api_utl'
   
config={
    'development': DevelopmentConfig
}
