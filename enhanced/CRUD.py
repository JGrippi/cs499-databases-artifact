"""
CRUD.py
This module provides a class for interacting with the MongoDB animal shelter database.
It handles all database operations with proper error handling and data validation.
"""

from pymongo import MongoClient, ASCENDING, DESCENDING
from bson.objectid import ObjectId
from typing import Dict, List, Any, Optional, Union
import logging
import json
from bson import json_util

# Configure logging for database operations
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AnimalShelter:
    """Handles CRUD operations for the animal shelter database with data validation and error handling."""

    def __init__(self):
        """Initialize MongoDB connection and set up database configuration."""
        self.client = MongoClient('mongodb://localhost:27017')
        self.database = self.client['AAC']
        self.collection = self.database['animals']
        self._setup_indexes()

    def _setup_indexes(self) -> None:
        """Create database indexes for optimized query performance."""
        try:
            self.collection.create_index([('breed', ASCENDING)])
            self.collection.create_index([('sex_upon_outcome', ASCENDING)])
            self.collection.create_index([('age_upon_outcome_in_weeks', ASCENDING)])
            self.collection.create_index([
                ('breed', ASCENDING),
                ('sex_upon_outcome', ASCENDING),
                ('age_upon_outcome_in_weeks', ASCENDING)
            ])
        except Exception as e:
            logger.warning(f"Index creation warning (can be ignored if indexes exist): {str(e)}")

    def _sanitize_document(self, doc: Dict) -> Dict:
        """Remove ObjectId and prepare document for JSON serialization."""
        if doc and '_id' in doc:
            del doc['_id']
        return doc

    def create(self, data: Dict[str, Any]) -> bool:
        """
        Create a new animal record in the database.
        
        Args:
            data: Dictionary containing animal data
            
        Returns:
            bool: True if creation successful, False otherwise
        """
        if not isinstance(data, dict):
            raise ValueError("Data must be a dictionary")

        required_fields = ['animal_id', 'breed', 'sex_upon_outcome']
        if not all(field in data for field in required_fields):
            raise ValueError(f"Missing required fields: {required_fields}")

        try:
            result = self.collection.insert_one(data)
            return bool(result.inserted_id)
        except Exception as e:
            logger.error(f"Error creating document: {str(e)}")
            return False

    def read(self, query: Dict[str, Any], page: int = 1, page_size: int = 10, sort_by: list = None) -> Dict[str, Any]:
        """
        Read animal records with pagination, sorting, and metadata.
        
        Args:
            query: MongoDB query dictionary
            page: Page number for pagination
            page_size: Number of records per page
            sort_by: List of sorting criteria
            
        Returns:
            Dictionary containing data and metadata
        """
        if not isinstance(query, dict):
            raise ValueError("Query must be a dictionary")
    
        try:
            page_size = int(page_size)
            total_docs = self.collection.count_documents(query)
            total_pages = max(1, -(-total_docs // page_size))
            page = max(1, min(page, total_pages))
            skip = (page - 1) * page_size
            
            cursor = self.collection.find(query)
            
            if sort_by:
                sort_list = []
                for sort_config in sort_by:
                    direction = ASCENDING if sort_config['direction'] == 'asc' else DESCENDING
                    sort_list.append((sort_config['column_id'], direction))
                if sort_list:
                    cursor = cursor.sort(sort_list)
            
            cursor = cursor.skip(skip).limit(page_size * 2)
            
            results = [self._sanitize_document(doc) for doc in cursor]
            unique_results = []
            seen_ids = set()
            
            for doc in results:
                if doc['animal_id'] not in seen_ids:
                    seen_ids.add(doc['animal_id'])
                    unique_results.append(doc)
                    if len(unique_results) == page_size:
                        break
            
            return {
                'data': unique_results,
                'metadata': {
                    'total_documents': total_docs,
                    'total_pages': total_pages,
                    'current_page': page,
                    'page_size': page_size,
                    'has_next': page < total_pages,
                    'has_prev': page > 1
                }
            }
        except Exception as e:
            logger.error(f"Error reading documents: {str(e)}")
            return {'data': [], 'metadata': {
                'total_documents': 0,
                'total_pages': 1,
                'current_page': 1,
                'page_size': page_size,
                'has_next': False,
                'has_prev': False
            }}

    def update(self, query: Dict[str, Any], update_data: Dict[str, Any]) -> int:
        """
        Update animal records matching the query.
        
        Args:
            query: MongoDB query to match documents
            update_data: Data to update in matched documents
            
        Returns:
            Number of documents modified
        """
        if not isinstance(query, dict) or not isinstance(update_data, dict):
            raise ValueError("Query and update_data must be dictionaries")

        try:
            result = self.collection.update_many(
                query,
                {'$set': update_data}
            )
            return result.modified_count
        except Exception as e:
            logger.error(f"Error updating documents: {str(e)}")
            return 0

    def delete(self, query: Dict[str, Any]) -> int:
        """
        Delete animal records matching the query.
        
        Args:
            query: MongoDB query to match documents for deletion
            
        Returns:
            Number of documents deleted
        """
        if not isinstance(query, dict):
            raise ValueError("Query must be a dictionary")

        try:
            result = self.collection.delete_many(query)
            return result.deleted_count
        except Exception as e:
            logger.error(f"Error deleting documents: {str(e)}")
            return 0

    def aggregate_stats(self, rescue_type: Optional[str] = None) -> Dict[str, Any]:
        """
        Calculate aggregated statistics for animals, optionally filtered by rescue type.
        
        Args:
            rescue_type: Optional filter for specific rescue animal types
            
        Returns:
            Dictionary containing aggregated statistics
        """
        base_pipeline = []
        
        if rescue_type:
            criteria = {
                "Water Rescue": {
                    "breeds": ["Labrador Retriever Mix", "Chesapeake Bay Retriever", "Newfoundland"],
                    "sex": "Intact Female",
                    "age_min": 26,
                    "age_max": 156
                },
                "Mountain Rescue": {
                    "breeds": ["German Shepherd", "Alaskan Malamute", "Old English Sheepdog", 
                             "Siberian Husky", "Rottweiler"],
                    "sex": "Intact Male",
                    "age_min": 26,
                    "age_max": 156
                },
                "Disaster Rescue": {
                    "breeds": ["Doberman Pinscher", "German Shepherd", "Golden Retriever", 
                             "Bloodhound", "Rottweiler"],
                    "sex": "Intact Male",
                    "age_min": 20,
                    "age_max": 300
                }
            }
            
            if rescue_type in criteria:
                rescue_criteria = criteria[rescue_type]
                base_pipeline.append({
                    "$match": {
                        "breed": {"$in": rescue_criteria["breeds"]},
                        "sex_upon_outcome": rescue_criteria["sex"],
                        "age_upon_outcome_in_weeks": {
                            "$gte": rescue_criteria["age_min"],
                            "$lte": rescue_criteria["age_max"]
                        }
                    }
                })

        try:
            pipeline = base_pipeline + [
                {
                    "$group": {
                        "_id": None,
                        "total_animals": {"$sum": 1},
                        "avg_age": {"$avg": "$age_upon_outcome_in_weeks"},
                        "breeds": {"$addToSet": "$breed"}
                    }
                },
                {
                    "$project": {
                        "_id": 0,
                        "total_animals": 1,
                        "avg_age": 1,
                        "breeds": 1
                    }
                }
            ]
            
            result = list(self.collection.aggregate(pipeline))
            if result:
                stats = result[0]
                stats['breeds'] = sorted(stats['breeds'])
                return stats
            return {"total_animals": 0, "avg_age": 0, "breeds": []}
            
        except Exception as e:
            logger.error(f"Error performing aggregation: {str(e)}")
            return {"total_animals": 0, "avg_age": 0, "breeds": []}