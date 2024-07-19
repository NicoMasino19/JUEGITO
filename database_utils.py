# database_utils.py

import psycopg2
from psycopg2 import sql
from datetime import datetime

def connect_to_db():
    try:
        connection = psycopg2.connect(
            dbname="railway",
            user="postgres",
            password="cIsnRwDUIvHaSZibyCUkJMRIKvqzBStB",
            host="viaduct.proxy.rlwy.net",
            port="46149"
        )
        return connection
    except (Exception, psycopg2.Error) as error:
        print("Error while connecting to PostgreSQL", error)
        return None

def save_score(player_name, score, playtime_seconds, difficulty):
    connection = connect_to_db()
    if connection:
        try:
            cursor = connection.cursor()
            current_time = datetime.now()
            insert_query = sql.SQL("""
                INSERT INTO MyTable (player_name, score, "playtime-seconds", difficulty, created_at)
                VALUES ({}, {}, {}, {}, {})
            """).format(
                sql.Literal(player_name), 
                sql.Literal(score),
                sql.Literal(playtime_seconds), 
                sql.Literal(difficulty),
                sql.Literal(current_time)
            )
            cursor.execute(insert_query)
            connection.commit()
            print("Score saved successfully")
        except (Exception, psycopg2.Error) as error:
            print("Error while saving score:", error)
        finally:
            if connection:
                cursor.close()
                connection.close()

def get_high_scores(limit=10):
    connection = connect_to_db()
    if connection:
        try:
            cursor = connection.cursor()
            select_query = sql.SQL("""
                SELECT player_name, score 
                FROM mytable 
                ORDER BY score DESC 
                LIMIT {}
            """).format(sql.Literal(limit))
            cursor.execute(select_query)
            high_scores = cursor.fetchall()
            return high_scores
        except (Exception, psycopg2.Error) as error:
            print("Error while fetching high scores:", error)
            return []
        finally:
            if connection:
                cursor.close()
                connection.close()
    else:
        print("Failed to connect to the database")
        return []