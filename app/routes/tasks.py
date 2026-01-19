from flask import Blueprint, request, jsonify, g
from app.models import Task, User
from app.schemas import TaskSchema
from app import db
from app.middleware import token_required
from marshmallow import ValidationError
from datetime import datetime

tasks_bp = Blueprint('tasks', __name__)

@tasks_bp.route('', methods=['POST'])
@token_required
def create_task():
    data = request.get_json()
    schema = TaskSchema()
    try:
        data = schema.load(data)
    except ValidationError as err:
        return jsonify(err.messages), 400

    new_task = Task(
        title=data['title'],
        description=data.get('description'),
        status=data.get('status', 'pending'),
        priority=data.get('priority'),
        due_date=data.get('due_date'),
        created_by=g.user.id,
        assignee_id=data.get('assignee_id')
    )
    
    db.session.add(new_task)
    db.session.commit()

    return jsonify({'message': 'Task created', 'task_id': new_task.id}), 201

@tasks_bp.route('', methods=['GET'])
@token_required
def get_all_tasks():
    # Filtering
    status = request.args.get('status')
    priority = request.args.get('priority')
    search = request.args.get('search')
    
    query = Task.query

    # Authorization: Users see own tasks (created or assigned), Admin sees all
    if g.user.role != 'admin':
        query = query.filter((Task.created_by == g.user.id) | (Task.assignee_id == g.user.id))

    if status:
        query = query.filter_by(status=status)
    if priority:
        query = query.filter_by(priority=priority)
    if search:
        query = query.filter(Task.title.contains(search) | Task.description.contains(search))
        
    tasks = query.all()
    
    result = []
    for task in tasks:
        result.append({
            'id': task.id,
            'title': task.title,
            'description': task.description,
            'status': task.status,
            'priority': task.priority,
            'due_date': task.due_date,
            'created_by': task.created_by,
            'assignee_id': task.assignee_id
        })
        
    return jsonify(result), 200

@tasks_bp.route('/<int:id>', methods=['GET'])
@token_required
def get_single_task(id):
    task = Task.query.get_or_404(id)
    
    # Auth: Creator, assignee, or admin only
    if g.user.role != 'admin' and task.created_by != g.user.id and task.assignee_id != g.user.id:
        return jsonify({'message': 'Permission denied'}), 403
        
    return jsonify({
        'id': task.id,
        'title': task.title,
        'description': task.description,
        'status': task.status,
        'priority': task.priority,
        'due_date': task.due_date,
        'created_by': task.created_by,
        'assignee_id': task.assignee_id
    }), 200

@tasks_bp.route('/<int:id>', methods=['PUT'])
@token_required
def update_task(id):
    task = Task.query.get_or_404(id)
    data = request.get_json()
    
    # Authorization logic
    is_admin = g.user.role == 'admin'
    is_creator = task.created_by == g.user.id
    is_assignee = task.assignee_id == g.user.id
    
    if not (is_admin or is_creator or is_assignee):
        return jsonify({'message': 'Permission denied'}), 403

    schema = TaskSchema(partial=True)
    try:
        data = schema.load(data)
    except ValidationError as err:
        return jsonify(err.messages), 400

    # Logic: Assignee update status only, Creator/Admin update all
    if is_assignee and not (is_admin or is_creator):
        # Assignee can ONLY update status
        # If they try to update anything else, we should either ignore it or error.
        # "Assignee: update status only"
        if set(data.keys()) - {'status'}:
             return jsonify({'message': 'Assignee can only update status'}), 403
        task.status = data.get('status', task.status)
        
    else:
        # Admin or Creator can update everything
        task.title = data.get('title', task.title)
        task.description = data.get('description', task.description)
        task.status = data.get('status', task.status)
        task.priority = data.get('priority', task.priority)
        task.due_date = data.get('due_date', task.due_date)
        if 'assignee_id' in data:
            task.assignee_id = data['assignee_id']

    db.session.commit()
    return jsonify({'message': 'Task updated'}), 200

@tasks_bp.route('/<int:id>', methods=['DELETE'])
@token_required
def delete_task(id):
    task = Task.query.get_or_404(id)
    
    # Creator or admin only
    if g.user.role != 'admin' and task.created_by != g.user.id:
        return jsonify({'message': 'Permission denied'}), 403
        
    db.session.delete(task)
    db.session.commit()
    return jsonify({'message': 'Task deleted'}), 200

@tasks_bp.route('/stats', methods=['GET'])
@token_required
def task_stats():
    # Return: total tasks, completed, pending, by priority
    # Different stats for users vs admins
    # Admin: All tasks
    # User: Own tasks
    
    query = Task.query
    if g.user.role != 'admin':
        query = query.filter((Task.created_by == g.user.id) | (Task.assignee_id == g.user.id))
        
    tasks = query.all()
    
    total = len(tasks)
    completed = len([t for t in tasks if t.status == 'completed'])
    pending = len([t for t in tasks if t.status == 'pending'])
    high_priority = len([t for t in tasks if t.priority == 'high'])
    
    return jsonify({
        'total_tasks': total,
        'completed_tasks': completed,
        'pending_tasks': pending,
        'high_priority_tasks': high_priority
    }), 200
