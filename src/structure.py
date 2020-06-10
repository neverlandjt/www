from pyspark.sql.types import StructType, StructField, StringType, DateType, IntegerType, ArrayType, BooleanType, \
    TimestampType, LongType, FloatType

metaSchema = StructType([
    StructField("uri", StringType(), True),
    StructField("request_id", StringType(), True),
    StructField("id", StringType(), True),
    StructField("dt", StringType(), True),
    StructField("domain", StringType(), True),
    StructField("stream", StringType(), True),
    StructField("topic", StringType(), True),
    StructField("partition", IntegerType(), True),
    StructField("offset", LongType(), True)
])

performerSchema = StructType([
    StructField("user_text", StringType(), True),
    StructField("user_groups", ArrayType(StringType()), True),
    StructField("user_is_bot", BooleanType(), True),
    StructField("user_id", LongType(), True),
    StructField("user_registration_dt", StringType(), True),
    StructField("user_edit_count", LongType(), True)
])

schema = StructType([
    StructField("$schema", StringType(), True),
    StructField("meta", metaSchema, True),
    StructField("database", StringType(), True),
    StructField("page_id", StringType(), True),
    StructField("page_title", StringType(), True),
    StructField("page_namespace", LongType(), True),
    StructField("rev_id", StringType(), True),
    StructField("rev_timestamp", StringType(), True),
    StructField("rev_sha1", StringType(), True),
    StructField("rev_minor_edit", BooleanType(), True),
    StructField("rev_len", LongType(), True),
    StructField("rev_content_model", StringType(), True),
    StructField("rev_content_format", StringType(), True),
    StructField("performer", performerSchema, True),
    StructField("page_is_redirect", BooleanType(), True),
    StructField("comment", StringType(), True),
    StructField("parsedcomment", StringType(), True)
])
