from datetime import timedelta
from logging import exception

from pyspark.sql import SparkSession
from pyspark.sql import functions as F


def main():
    spark = (
        SparkSession.builder
        .appName("net_ratio_10m")
        .getOrCreate()
    )

    # https://docs.cloudera.com/cdp-private-cloud-base/7.1.8/spark-overview/topics/spark-unsupported-features.html
    # https://stackoverflow.com/questions/43759534/java-lang-numberformatexception-caused-by-spark-jdbc-reading-table-header
    jvm = spark._jvm
    JdbcDialects = jvm.org.apache.spark.sql.jdbc.JdbcDialects
    Hive2Dialect = jvm.hive2.Hive2Dialect
    JdbcDialects.registerDialect(Hive2Dialect())

    jdbc_url = "jdbc:hive2://hive:10000/default"
    hive_driver = "org.apache.hive.jdbc.HiveDriver"

    df_raw = (
        spark.read
        .format("jdbc")
        .option("url", jdbc_url)
        .option("driver", hive_driver)
        .option("dbtable", "raw_metrics")
        .load()
    )

    prefix = "raw_metrics."
    for col in df_raw.columns:
        if col.startswith(prefix):
            df_raw = df_raw.withColumnRenamed(col, col[len(prefix):])

    df_raw = df_raw.select("timestamp", "net_in_total_mb", "net_out_total_mb")

    df_raw = df_raw.withColumn("timestamp_ts", F.to_timestamp("timestamp"))
    df_raw = (
        df_raw
        .drop("timestamp")
        .withColumnRenamed("timestamp_ts", "timestamp")
    )

    df_raw = df_raw.withColumn(
        "ratio_in_out",
        F.col("net_in_total_mb") / F.col("net_out_total_mb")
    )

    print("=== RAW AFTER LOAD ===\n", "RAW COUNT: ", df_raw.count())
    df_raw.orderBy("timestamp").show(5, truncate=False)
    print("======================")

    max_ts_row = df_raw.agg(F.max("timestamp").alias("max_ts")).collect()[0]
    max_ts = max_ts_row["max_ts"]

    if max_ts is None:
        print("!!! raw_metrics table is empty !!!")
        spark.stop()
        return

    window_end = max_ts
    window_start = max_ts - timedelta(minutes=10)

    print(f"Window:\nstart = {window_start}\nend = {window_end}")

    df_window = df_raw.filter(
        (F.col("timestamp") > F.lit(window_start)) &
        (F.col("timestamp") <= F.lit(window_end))
    )

    print("POINTS IN WINDOW:", df_window.count())
    df_window.orderBy("timestamp").show(20, truncate=False)

    from pyspark.sql.functions import expr

    df_agg = (
        df_window
        .agg(
            expr(f"min(timestamp) as window_start_ts"),
            expr(f"max(timestamp) as window_end_ts"),
            expr("count(*) as points_count"),
            expr("avg(ratio_in_out) as avg_ratio_in_out")
        )
    )

    print("=== AGG TO WRITE ===")
    df_agg.show(truncate=False)

    rows = df_agg.collect()
    if rows:
        jvm.java.lang.Class.forName(hive_driver)
        conn = jvm.java.sql.DriverManager.getConnection(jdbc_url, "", "")
        stmt = conn.createStatement()

        for r in rows:
            ws = str(r["window_start_ts"])
            we = str(r["window_end_ts"])
            cnt = int(r["points_count"])
            avg = float(r["avg_ratio_in_out"])

            sql = (
                "INSERT INTO net_ratio_10m "
                "(window_start_ts, window_end_ts, points_count, avg_ratio_in_out) "
                f"VALUES ('{ws}', '{we}', {cnt}, {avg})"
            )

            stmt.executeUpdate(sql)

        stmt.close()
        conn.close()
        print("=== DONE ===")
    else:
        print("!!! SOMETHING WENT WRONG !!!")

    spark.stop()


if __name__ == "__main__":
    main()
