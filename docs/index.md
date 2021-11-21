# YETL Framework

Yet another ETL Framework for Spark


How does it work?

Declaritive spark dataframe pipelining frameworking.

1. Define your datastores e.g. `./project/datastores`
2. Define your datasets e.g. `./project/datasets`
3. Write spark extract, transform and load in sql, python or scala just referencing a dataset using yetl api. Api can also be used by orchestration tools to land data from source for spark
4. Create datastore, datasets and workflow documentation automatically
5. Execute workflows compiled from code dataset references in a basic execution engine or other tools e.g. databricks mulistep jobs etc

Progress log:

* 2021-11-21: Done : Metadata design 1st draft prototype
* WIP: Jinja2 Templating and Deserialization: WIP

## Philosophical Goals

- Have fun learning and building something that has no affiliation to anything commercial
- Easy and fun to engineer pipelines
- Can be used in spark everywhere (Spark PaaS, IaaS, baremetal, locally)
- Bar landing the data in the cloud spark is all we need
- Excellent metadata configuration and tools - fun, simple, full featured and minimal
- No data loading anti-patterns resulting from poorly designed re-use and metadata
- Can be called if desired seamlessly from any workflow tool integrating transparent lineage
- Fully and easily testable locally and remotely
- Support batch and streaming
- Support datalake house add-on's - hudi, deltalake


## Feature Goals


- Extremely Flexible
- Support Behavior Driven Development
- Support Test Driven Developement
- Integrate and Support Data Expectation Frameworks
- Workflow Engine
- Auto Document Pipelines