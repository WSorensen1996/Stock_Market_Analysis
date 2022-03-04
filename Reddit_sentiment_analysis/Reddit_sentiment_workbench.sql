-- CREATE DATABASE reddit_sentiment; 

use reddit_sentiment; 

-- DROP SCHEMA reddit_sentiment;

drop table Bearish;
drop table Bullish;
drop table Neutral;
drop table Total_Compound;
drop table Mentions;

-- select * from Bullish;
-- select * from Bearish;
-- select * from Neutral;
-- select * from Total_Compound;
-- select * from Mentions;


create table Bearish (Ticker varchar(10) not null);
create table Bullish (Ticker varchar(10) not null);
create table Neutral (Ticker varchar(10) not null);
create table Total_Compound (Ticker varchar(10) not null);
create table Mentions (Ticker varchar(10) not null);
 
SHOW tables; 


