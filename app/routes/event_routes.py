from flask import Blueprint, request, jsonify

from app.services.event_service import (
    get_all_events,
    create_event,
    update_event,
    delete_event,
    search_event,
    get_event_by_id,
)

event_bp = Blueprint("event", __name__)

# GET all events
@event_bp.route("/", methods=["GET"])
def list_events():
    """
    Get all events
    ---
    tags:
      - Events
    responses:
      200:
        description: List of all events
        schema:
          type: array
          items:
            type: object
    """
    try:
        events = get_all_events()
        return jsonify(events), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# GET single event by ID
@event_bp.route("/<event_id>", methods=["GET"])
def get_event(event_id):
    """
    Get a single event by ID
    ---
    tags:
      - Events
    parameters:
      - in: path
        name: event_id
        required: true
        type: string
    responses:
      200:
        description: Event found
      404:
        description: Event not found
    """
    try:
        event = get_event_by_id(event_id)
        if not event:
            return jsonify({"error": "Event not found"}), 404
        return jsonify(event), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# POST create new event
@event_bp.route("/", methods=["POST"])
def add_event():
    """
    Create a new event
    ---
    tags:
      - Events
    consumes:
      - application/json
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            title:
              type: string
            date:
              type: string
            time:
              type: string
            description:
              type: string
    responses:
      201:
        description: Event created successfully
      400:
        description: Invalid input
    """
    try:
        data = request.get_json()
        new_event = create_event(data)
        return jsonify(new_event), 201
    except ValueError as ve:
        return jsonify({"error": str(ve)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# PUT update event
@event_bp.route("/<event_id>", methods=["PUT"])
def edit_event(event_id):
    """
    Update an existing event
    ---
    tags:
      - Events
    consumes:
      - application/json
    parameters:
      - in: path
        name: event_id
        required: true
        type: string
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            title:
              type: string
            date:
              type: string
            time:
              type: string
            description:
              type: string
    responses:
      200:
        description: Event updated successfully
      404:
        description: Event not found
    """
    try:
        data = request.get_json()
        updated_event = update_event(event_id, data)
        return jsonify(updated_event), 200
    except ValueError as ve:
        return jsonify({"error": str(ve)}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# DELETE event
@event_bp.route("/<event_id>", methods=["DELETE"])
def remove_event(event_id):
    """
    Delete an event
    ---
    tags:
      - Events
    parameters:
      - in: path
        name: event_id
        required: true
        type: string
    responses:
      200:
        description: Event deleted successfully
      404:
        description: Event not found
    """
    try:
        delete_event(event_id)
        return jsonify({"message": "Event deleted"}), 200
    except ValueError as ve:
        return jsonify({"error": str(ve)}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# PATCH partial update event
@event_bp.route("/<event_id>", methods=["PATCH"])
def partial_update_event(event_id):
    """
    Partially update an existing event
    ---
    tags:
      - Events
    consumes:
      - application/json
    parameters:
      - in: path
        name: event_id
        required: true
        type: string
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            title:
              type: string
            date:
              type: string
            time:
              type: string
            description:
              type: string
    responses:
      200:
        description: Event updated successfully
      404:
        description: Event not found
    """
    try:
        data = request.get_json()
        updated_event = update_event(event_id, data, partial=True)
        return jsonify(updated_event), 200
    except ValueError as ve:
        return jsonify({"error": str(ve)}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@event_bp.route("/search", methods=["GET"])
def search():
    """
    Search events by title or description
    ---
    tags:
      - Events
    parameters:
      - name: query
        in: query
        type: string
        required: true
    responses:
      200:
        description: Matching events
    """
    query = request.args.get("q", "").strip()
    if not query:
        return jsonify({"error": "Search query `q` is required"}), 400

    try:
        matches = search_event(query)
        return jsonify(matches), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
