ThisBuild / scalaVersion := "2.12.18"
ThisBuild / version := "0.1.0"
ThisBuild / organization := "my.spark"

lazy val root = (project in file("."))
  .settings(
    name := "hive2-dialect",
    libraryDependencies += "org.apache.spark" %% "spark-sql" % "3.5.0" % "provided",
    Compile / unmanagedSourceDirectories += baseDirectory.value / "hive2"
  )
