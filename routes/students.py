from flask import Blueprint, request, jsonify
from routes.books import books_bp
from models import db, Student, Book, StudentBook
from datetime import datetime

students_bp = Blueprint('students', __name__)

# 🔹 Récupérer tous les étudiants (avec pagination)
@students_bp.route('/students', methods=['GET'])
def get_students():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)

    students = Student.query.paginate(page=page, per_page=per_page, error_out=False)

    return jsonify({
        'total': students.total,
        'page': students.page,
        'per_page': students.per_page,
        'students': [
            {'id': s.id, 'first_name': s.first_name, 'last_name': s.last_name, 
             'birth_date': s.birth_date.strftime('%Y-%m-%d') if s.birth_date else None,
             'email': s.email}
            for s in students.items
        ]
    })

# 🔹 Récupérer un étudiant par ID
@students_bp.route('/students/<int:id>', methods=['GET'])
def get_student(id):
    student = Student.query.get_or_404(id, description="Student not found")
    return jsonify({
        'id': student.id,
        'first_name': student.first_name,
        'last_name': student.last_name,
        'birth_date': student.birth_date.strftime('%Y-%m-%d') if student.birth_date else None,
        'email': student.email
    })

# 🔹 Ajouter un étudiant
@students_bp.route('/students', methods=['POST'])
def add_student():
    data = request.get_json()

    if not data or 'first_name' not in data or 'last_name' not in data or 'email' not in data:
        return jsonify({'error': 'Invalid data, first_name, last_name, and email are required'}), 400

    birth_date = None
    if 'birth_date' in data:
        try:
            birth_date = datetime.strptime(data['birth_date'], '%Y-%m-%d')
        except ValueError:
            return jsonify({'error': 'Invalid date format, expected YYYY-MM-DD'}), 400

    student = Student(
        first_name=data['first_name'], 
        last_name=data['last_name'], 
        email=data['email'], 
        birth_date=birth_date
    )

    db.session.add(student)
    db.session.commit()
    return jsonify({'message': 'Student added successfully', 'id': student.id}), 201

# 🔹 Mettre à jour un étudiant
@students_bp.route('/students/<int:id>', methods=['PUT'])
def update_student(id):
    student = Student.query.get_or_404(id, description="Student not found")

    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400

    if 'first_name' in data:
        student.first_name = data['first_name']
    if 'last_name' in data:
        student.last_name = data['last_name']
    if 'email' in data:
        student.email = data['email']
    if 'birth_date' in data:
        try:
            student.birth_date = datetime.strptime(data['birth_date'], '%Y-%m-%d')
        except ValueError:
            return jsonify({'error': 'Invalid date format, expected YYYY-MM-DD'}), 400

    db.session.commit()
    return jsonify({'message': 'Student updated successfully'})

# 🔹 Supprimer un étudiant
@students_bp.route('/students/<int:id>', methods=['DELETE'])
def delete_student(id):
    student = Student.query.get_or_404(id, description="Student not found")

    db.session.delete(student)
    db.session.commit()
    return jsonify({'message': 'Student deleted successfully'})

# 🔹 Récupérer les livres empruntés par un étudiant
@students_bp.route('/students/<int:id>/borrowed_books', methods=['GET'])
def get_borrowed_books_for_student(id):
    records = StudentBook.query.filter_by(student_id=id, return_date=None).all()
    result = []
    for record in records:
        book = Book.query.get(record.book_id)
        result.append({
            'book_id': book.id,
            'title': book.title,
            'borrow_date': record.borrow_date.strftime('%Y-%m-%d')
        })
    return jsonify(result)


@books_bp.route('/books/borrowed', methods=['GET'])
def get_borrowed_books():
    borrowed = StudentBook.query.filter_by(return_date=None).all()
    
    result = []
    for record in borrowed:
        book = Book.query.get(record.book_id)
        result.append({
            'book_id': book.id,
            'title': book.title,
            'author': book.author,
            'borrow_date': record.borrow_date.strftime('%Y-%m-%d'),
            'borrower_id': record.student_id
        })
    
    return jsonify(result)

@books_bp.route('/borrow', methods=['POST'])
def borrow_book():
    data = request.get_json()

    student_id = data.get('student_id')
    book_id = data.get('book_id')

    if not student_id or not book_id:
        return jsonify({'error': 'student_id and book_id are required'}), 400

    # Vérifie si le livre est déjà emprunté (non retourné)
    existing_borrow = StudentBook.query.filter_by(book_id=book_id, return_date=None).first()
    if existing_borrow:
        return jsonify({'error': 'Book is already borrowed'}), 409

    # Crée le lien entre l’élève et le livre
    borrow = StudentBook(
        student_id=student_id,
        book_id=book_id,
        borrow_date=datetime.utcnow()
    )
    db.session.add(borrow)
    db.session.commit()

    return jsonify({'message': 'Book successfully borrowed'})
