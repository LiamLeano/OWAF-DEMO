--
-- File generated with SQLiteStudio v3.4.4 on Fri Mar 28 18:46:21 2025
--
-- Text encoding used: UTF-8
--
PRAGMA foreign_keys = off;
BEGIN TRANSACTION;

-- Table: audio
CREATE TABLE IF NOT EXISTS audio (audio_id integer PRIMARY KEY AUTOINCREMENT, name varchar (255) NOT NULL, year integer, artist varchar (255), topic varchar (255) NOT NULL DEFAULT Audio, category varchar (255) NOT NULL, type varchar (255) NOT NULL, record_label varchar (255), media_piece_path varchar (255), screenshot_path varchar (255), file_name varchar (255), file_size float, data_metric varchar (255), source_link text, download_link text, magnet_link text, sha256 varchar (64), sha1 varchar (40), md5 varchar (32), crc32 varchar (8));

-- Table: documents
CREATE TABLE IF NOT EXISTS documents (documents_id integer PRIMARY KEY AUTOINCREMENT, name varchar (255) NOT NULL, year integer, author varchar (255), topic varchar (255) NOT NULL DEFAULT Documents, category varchar (255) NOT NULL, type varchar (255) NOT NULL, publisher varchar (255), media_piece_path varchar (255), screenshot_path varchar (255), file_name varchar (255), file_size float, data_metric varchar (255), source_link text, download_link text, magnet_link text, sha256 varchar (64), sha1 varchar (40), md5 varchar (32), crc32 varchar (8));

-- Table: politics
CREATE TABLE IF NOT EXISTS politics (politics_id INTEGER PRIMARY KEY AUTOINCREMENT, name VARCHAR (255) NOT NULL, year INTEGER, politician VARCHAR (255), topic VARCHAR (255) NOT NULL DEFAULT 'Politics', category VARCHAR (255) NOT NULL, type VARCHAR (255) NOT NULL, news_company VARCHAR (255), media_piece_path VARCHAR (255), screenshot_path VARCHAR (255), file_name VARCHAR (255), file_size FLOAT, data_metric VARCHAR (255), source_link TEXT, download_link TEXT, magnet_link TEXT, sha256 VARCHAR (64), sha1 VARCHAR (40), md5 VARCHAR (32), crc32 VARCHAR (8));

-- Table: software
CREATE TABLE IF NOT EXISTS software (software_id integer PRIMARY KEY AUTOINCREMENT, name varchar (255) NOT NULL, year integer, developer varchar (255), topic varchar (255) NOT NULL DEFAULT Software, category varchar (255) NOT NULL, type varchar (255) NOT NULL, architecture varchar (255), media_piece_path varchar (255), screenshot_path varchar (255), file_name varchar (255), file_size float, data_metric varchar (255), source_link text, download_link text, magnet_link text, sha256 varchar (64), sha1 varchar (40), md5 varchar (32), crc32 varchar (8));

-- Table: videos
CREATE TABLE IF NOT EXISTS videos (videos_id integer PRIMARY KEY AUTOINCREMENT, name varchar (255) NOT NULL, year integer, director varchar (255), topic varchar (255) NOT NULL DEFAULT Videos, category varchar (255) NOT NULL, type varchar (255) NOT NULL, company varchar (255), media_piece_path varchar (255), screenshot_path varchar (255), file_name varchar (255), file_size float, data_metric varchar (255), source_link text, download_link text, magnet_link text, sha256 varchar (64), sha1 varchar (40), md5 varchar (32), crc32 varchar (8));

COMMIT TRANSACTION;
PRAGMA foreign_keys = on;
