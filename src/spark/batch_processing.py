import time
from structure import schema
from pyspark.sql.types import StringType, BooleanType
from pyspark.sql import SparkSession, SQLContext, Window
from pyspark.sql.functions import col, from_json, window, month, dayofmonth, minute, hour, arrays_overlap, lit, array, \
    to_json, udf, collect_list, struct, first, explode, count, lit, desc
from datetime import datetime, timedelta
import pyspark.sql.functions as f

if __name__ == '__main__':
    kafka_hosts = "172.31.64.180:9092,172.31.70.161:9092,172.31.64.76:9092"

    cassandra_cluster = '172.31.35.107'
    spark = SparkSession.builder.appName('WikiApp').config('spark.cassandra.connection.host', cassandra_cluster) \
        .config("spark.cassandra.auth.username", "cassandra") \
        .config("spark.cassandra.auth.password", "cassandra").getOrCreate()

    spark.conf.set('spark.sql.streaming.checkpointLocation', '/home/ubuntu/checkpoint')

    mtime_to_date = udf(lambda date: time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(date / 1000)), StringType())

    df = spark.read \
        .format("kafka") \
        .option("kafka.bootstrap.servers", kafka_hosts) \
        .option('topic', 'wiki') \
        .option("subscribe", "wiki") \
        .option("startingOffsets", 'earliest') \
        .load()

    now = datetime.now()
    upper = now - timedelta(minutes=now.minute, seconds=now.second, microseconds=now.microsecond)
    lower = upper - timedelta(hours=6)
    bounds = udf(lambda x: lower < x < upper, BooleanType())

    ds = df.select(from_json(col("value").cast("string"), schema).alias('value')) \
        .selectExpr('value.*').filter(bounds("meta.dt"))

    first_query = ds.withColumn("time_start", hour("meta.dt")).groupBy("time_start", "meta.domain").agg(
        count("meta.domain").alias('created_pages')).orderBy(desc("created_pages")).groupBy('time_start').agg(
        collect_list(struct(col("domain"), "created_pages")).alias("statistics")).withColumn(
        "time_end", col("time_start") + 1)

    second_query = ds.groupBy("meta.domain").agg(
        f.sum(col("performer.user_is_bot").cast('long')).alias("created_by_bots")).orderBy(desc("created_by_bots")) \
        .select(lit(lower.hour).alias("time_start"), lit(upper.hour).alias("time_end"),
                collect_list(struct(col("domain"), col("created_by_bots"))).alias('statistics'))

    third_query = ds.select(col("performer.user_id").alias("user_id"),
                            col("performer.user_text").alias("user_name"), "page_title").groupBy("user_id") \
        .agg(first("user_name").alias("user_name"), count(col("user_id")).alias("number_of_pages"),
             collect_list(col("page_title")).alias("page_titles")).orderBy(
        desc("number_of_pages")).limit(20) \
        .select(lit(lower.hour).alias("time_start"), lit(upper.hour).alias("time_end"),
                collect_list(struct("user_id", "user_name", "number_of_pages",
                                    "page_titles")).alias("users"))

    first_query.write.format("org.apache.spark.sql.cassandra") \
        .options(keyspace='project', table='stats_created_pages') \
        .mode('append') \
        .save()

    second_query.write.format("org.apache.spark.sql.cassandra") \
        .options(keyspace='project', table='stats_domains') \
        .mode('append') \
        .save()

    third_query.write.format("org.apache.spark.sql.cassandra") \
        .options(keyspace='project', table='stats_users') \
        .mode('append') \
        .save()
