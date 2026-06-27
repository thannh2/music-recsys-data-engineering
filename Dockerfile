FROM bitnamilegacy/spark:3.3.2
USER root
RUN pip install pymongo
USER 1001