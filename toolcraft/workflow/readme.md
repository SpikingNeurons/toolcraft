Here we will have workflow builder

Reference
https://stackoverflow.com/questions/48986732/airflow-creating-a-dag-in-airflow-via-ui


CWL is just a specification.
CWL can be used to write workflows.
These CWL workflows can be translated Airflow DAGs
Then we can edit these CWL in rabix composer https://github.com/rabix/composer


Rabix composer looks promising


Or may be HashableCLass is already powerful to build interactive workflows
 ... Like Dataset already what datasets are there ... for Model we can have a
  special class which reads python file to build Model based on custom python
   code ;)

# more


Possible library name mlcraft https://pypi.org/project/mlcraft (already registered)

todo: integrate with mlflow, DvC, DagsHub

todo: try to mimic mlflow api as it uses flask and does basic file saves ...
  maybe we can better it with pyarrow, fsspec, arrow flight rpc etc.
  Also pyarrow dataframe search feature is more powerful and we have already
  integrated it in toolcraft

Check examples at https://github.com/mlflow/mlflow/tree/master/examples
Especially the hyperparams example. We can assign experiment ID as our hexhash of
m.HashableClass ... and then use mlflow-ui for parameter tuning

Note that you can also use mlflow to make conda environments and install required
packages ... also docker can be used
https://www.mlflow.org/docs/latest/models.html

It can also look at git tags to run multiple experiments

You can even serve models
https://www.mlflow.org/docs/latest/models.html#built-in-deployment-tools

It also has rest api and you can request to do more things in an experiment.
And we can also track more things ...
https://github.com/mlflow/mlflow/tree/master/examples/rest_api

You can build mlflow plugins and distribute it on pypi
https://mlflow.org/docs/latest/plugins.html#writing-your-own-mlflow-plugins

Integrate mlflow and airflow dags
https://medium.com/@amrkmrc/airflow-and-mlflow-integration-d93e193b8b74

Borrow decorator based ideas from IDSIA/sacred
https://github.com/IDSIA/sacred/tree/master/examples


MLOps tech stack ... as field is evolving monitor such things
https://ml-ops.org/content/state-of-mlops

DVC is other popular alternative to MLOps

DagsHub integration is useful where you can manage experiments alongside code, and
datasets and also share it to public. It has integration for mlflow and dvc
https://dagshub.com
https://towardsdatascience.com/use-mlflow-and-dvc-for-open-source-reproducible-machine-learning-2ab8c0678a94

DVC can work alongside mlops: https://medium.com/geekculture/comparing-metaflow-mlflow-and-dvc-e84be6db2e2
  Update: I was told by the DVC community that running MLflow and DVC together is also
    an option.(MLFlow for visualization, DVC for versioning). This approach could help
    mitigating the shortcomings of MLFlow regarding collaboration whilst using its
    powerful UI.
