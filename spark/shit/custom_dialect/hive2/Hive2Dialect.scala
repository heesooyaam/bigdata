package hive2

import org.apache.spark.sql.jdbc.JdbcDialect

class Hive2Dialect extends JdbcDialect {

  override def canHandle(url: String): Boolean =
    url != null && url.toLowerCase.startsWith("jdbc:hive2")

  private def stripQualifier(colName: String): String = {
    val idx = colName.lastIndexOf('.')
    if (idx >= 0 && idx < colName.length - 1) colName.substring(idx + 1)
    else colName
  }

  override def quoteIdentifier(colName: String): String = {
    val bare = stripQualifier(colName)
    s"`$bare`"
  }
}
