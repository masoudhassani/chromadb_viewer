import os, sys
import chromadb
from chromadb.config import Settings


class ChromadbConnector:
    def __init__(self, database_configs) -> None:
        self.database_configs = database_configs

        # connect to a local file or chroma server
        self._connect()

    def _connect(self):
        host = self.database_configs.get("host", "127.0.0.1")
        port = self.database_configs.get("port", "8009")  # Default MongoDB port
        auth_token = self.database_configs.get("auth_token", "")
        no_db_server = self.database_configs.get(
            "no_db_server", False
        )  # If True, connect to local file instead host and port

        if no_db_server:
            # if local is requested, script searches from chroma.db in the home directory
            # or it creates chroma.db if not available
            home_dir = os.path.expanduser("~")
            chromadb_path = os.path.join(home_dir, "chroma.db")

            print(f"connecting to {chromadb_path}")
            try:
                self.client = chromadb.PersistentClient(path=chromadb_path)
                print(f"connected")

            except Exception as e:
                print(f"error connecting to {chromadb_path} because {e}.\nexiting!")
                sys.exit(0)

        else:
            # if the user has requested a server setup for chromadb (host:port)
            print(f"connecting to chromadb at {host}:{port}")

            try:
                if auth_token:
                    self.client = chromadb.HttpClient(
                        host=host,
                        port=port,
                        settings=Settings(
                            chroma_client_auth_provider="chromadb.auth.token_authn.TokenAuthClientProvider",
                            chroma_client_auth_credentials=auth_token,
                        ),
                    )
                else:
                    self.client = chromadb.HttpClient(host=host, port=port)
                print(f"connected",
                )
            except Exception as e:
                print(f"error connecting to {host}:{port} because {e}.\nexiting!")
                sys.exit(0)

    def list_collections(self):
        """
        List all collections in the Chroma database.
        Returns:
            list: A list of collection names.
        """
        collections = self.client.list_collections()
        return [collection.name for collection in collections]

    def list_documents(self, collection_name):
        """
        List all documents in a specified collection.
        Args:
            collection_name (str): The name of the collection.
        Returns:
            list: A list of documents in the collection.
        """
        collection = self.client.get_collection(collection_name)
        if not collection:
            raise ValueError(f"Collection '{collection_name}' does not exist.")
        documents = collection.list_documents()
        return documents

    def query(self, collection_name, user_query, metadata=None):
        """
        Query a collection based on a user query and optional metadata.
        Args:
            collection_name (str): The name of the collection to query.
            user_query (str): The user query.
            metadata (dict, optional): Metadata filters for the query.
        Returns:
            list: Query results.
        """
        try:
            # Explicitly pass 'name' to avoid ambiguity
            collection = self.client.get_collection(name=collection_name)
            results = collection.query(query_texts=[user_query], where=metadata, n_results=50)

            return results
        except ValueError as e:
            raise ValueError(f"Error fetching collection: {str(e)}")
        except Exception as e:
            raise Exception(f"Unexpected error: {str(e)}")
