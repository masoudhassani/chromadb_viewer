from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from modules.chromadb_connector import ChromadbConnector
from math import ceil
import yaml
import argparse

app = Flask(__name__)
CORS(app)

parser = argparse.ArgumentParser()
parser.add_argument(
    "--environment",
    choices=["local", "cloud"],
    required=True,
    help="choose the environment: local, cloud.",
)
args = parser.parse_args()
environment = args.environment

with open("configs/environment_configs.yml", "r") as file:
    environment_configs = yaml.safe_load(file)[environment]
db = ChromadbConnector(database_configs=environment_configs["chromadb"])  # Initialize your ChromaDB connector

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/collections', methods=['GET'])
def get_collections():
    collections = db.list_collections()  # Fetch all collections
    return jsonify({'collections': collections})

@app.route('/documents', methods=['GET'])
def get_documents():
    collection_name = request.args.get('collection_name')
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 10))

    documents = db.list_documents(collection_name)  # Fetch documents from the collection
    total_docs = len(documents)
    total_pages = ceil(total_docs / per_page)
    paginated_docs = documents[(page - 1) * per_page: page * per_page]

    return jsonify({
        'documents': paginated_docs,
        'page': page,
        'total_pages': total_pages,
        'total_docs': total_docs
    })

@app.route("/query", methods=["POST"])
def query_database():
    data = request.json
    collection_name = data.get("collection")
    query = data.get("query")
    metadata = data.get("metadata", {})

    if not collection_name or not query:
        return jsonify({"error": "Collection and query are required"}), 400

    try:
        # Call the query function of the database connector
        raw_results = db.query(collection_name=collection_name, user_query=query, metadata=metadata)

        # Restructure the results into a list of individual results
        structured_results = [
            {"id": id_, "document": doc, "metadata": meta}
            for id_, doc, meta in zip(raw_results["ids"][0], raw_results["documents"][0], raw_results["metadatas"][0])
        ]

        return jsonify({"results": structured_results})
    except ValueError as e:
        app.logger.error(f"ValueError: {str(e)}")
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        app.logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        return jsonify({"error": "Internal server error"}), 500




if __name__ == '__main__':
    app.run(debug=True)
