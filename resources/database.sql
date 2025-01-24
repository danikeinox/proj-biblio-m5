USE library_system;

-- Eliminar tablas si existen
DROP TABLE IF EXISTS returns;
DROP TABLE IF EXISTS rents;
DROP TABLE IF EXISTS books_genres;
DROP TABLE IF EXISTS genres;
DROP TABLE IF EXISTS reservations;
DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS books;
DROP TABLE IF EXISTS editorial;
DROP TABLE IF EXISTS libraries;

-- Crear tablas
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100),
    username VARCHAR(100) UNIQUE,
    password VARCHAR(100), -- Recuerda almacenar contraseñas hasheadas
    is_admin BOOLEAN,
    rented_notification_seen BOOLEAN DEFAULT FALSE
);

CREATE TABLE editorial (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100),
    address VARCHAR(100),
    phone VARCHAR(20),
    email VARCHAR(100),
    website VARCHAR(100),
    country VARCHAR(100),
    city VARCHAR(100),
    postal_code VARCHAR(20)
);

CREATE TABLE libraries (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100),
    address VARCHAR(100),
    phone VARCHAR(20),
    email VARCHAR(100),
    website VARCHAR(100),
    country VARCHAR(100),
    city VARCHAR(100),
    postal_code VARCHAR(20)
);

CREATE TABLE genres (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) UNIQUE
);

CREATE TABLE books (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(100),
    author VARCHAR(100),
    editorial_id INT,
    available_qty INT DEFAULT 0,
    reserved INT DEFAULT 0,
    FOREIGN KEY (editorial_id) REFERENCES editorial(id)
);

CREATE TABLE books_genres (
    book_id INT,
    genre_id INT,
    PRIMARY KEY (book_id, genre_id),
    FOREIGN KEY (book_id) REFERENCES books(id) ON DELETE CASCADE,
    FOREIGN KEY (genre_id) REFERENCES genres(id) ON DELETE CASCADE
);

CREATE TABLE rents (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    book_id INT,
    time_rented TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status ENUM('rented', 'returned') DEFAULT 'rented',
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (book_id) REFERENCES books(id)
);

CREATE TABLE returns (
    id INT AUTO_INCREMENT PRIMARY KEY,
    rent_id INT UNIQUE,
    time_returned TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (rent_id) REFERENCES rents(id)
);

CREATE TABLE reservations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    book_id INT,
    time_reserved TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status ENUM('reserved', 'rented', 'notified', 'cancelled') DEFAULT 'reserved',
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (book_id) REFERENCES books(id)
);

-- Crear vistas
CREATE OR REPLACE VIEW books_view AS
SELECT b.id, b.title, b.author, e.name AS editorial, b.available_qty, b.reserved
FROM books b
JOIN editorial e ON b.editorial_id = e.id;

CREATE OR REPLACE VIEW rents_view AS
SELECT r.id, u.name AS user, b.title AS book, r.time_rented, r.status
FROM rents r
JOIN users u ON r.user_id = u.id
JOIN books b ON r.book_id = b.id;

CREATE OR REPLACE VIEW reservations_view AS
SELECT res.id, u.name AS user, b.title AS book, res.time_reserved, res.status
FROM reservations res
JOIN users u ON res.user_id = u.id
JOIN books b ON res.book_id = b.id;

-- Insertar datos
INSERT INTO libraries (name, address, phone, email, website, country, city, postal_code)
VALUES ('Biblioteca Nacional', 'Calle 123', '123456789', 'bnacional@biblioteca.com', 'www.bibliotecanacional.com',
        'Spain', 'Madrid', '28001'),
       ('Biblioteca de Catalunya', 'Calle 456', '987654321', 'bcat@biblioteca.com', 'www.bibliotecacatalunya.com',
        'Spain', 'Barcelona', '08001'),
       ('Biblioteca de Sevilla', 'Calle 789', '123456789', 'bsev@biblioteca.com', 'www.bibliotecasevilla.com', 'Spain',
        'Sevilla', '41001'),
       ('Biblioteca de Valencia', 'Calle 101112', '987654321', 'bval@biblioteca.com', 'www.bibliotecavalencia.com',
        'Spain', 'Valencia', '46001'),
       ('Biblioteca de Zaragoza', 'Calle 131415', '123456789', 'bzar@biblioteca.com', 'www.bibliotecazaragoza.com',
        'Spain', 'Zaragoza', '50001');

INSERT INTO editorial (name, address, phone, email, website, country, city, postal_code)
VALUES ('Editorial Planeta', 'Calle 123', '123456789', 'planeta@editorialplaneta.com', 'www.editorialplaneta.com',
        'Spain', 'Barcelona', '08001'),
       ('Editorial Santillana', 'Calle 456', '987654321', 'santillana@editorialsantillana.com',
        'www.editorialsantillana.com', 'Spain', 'Madrid', '28001'),
       ('Editorial Anaya', 'Calle 789', '123456789', 'anaya@editorialanaya.com', 'www.editorialanaya.com', 'Spain',
        'Valencia', '46001'),
       ('Editorial SM', 'Calle 101112', '987654321', 'sm@editorialsm.com', 'www.editorialsm.com', 'Spain', 'Sevilla',
        '41001'),
       ('Editorial Oxford', 'Calle 131415', '123456789', 'oxford@editorialoxford.com', 'www.editorialoxford.com',
        'Spain', 'Zaragoza', '50001');

INSERT INTO genres (name)
VALUES ('Fantasy'),
       ('Science Fiction'),
       ('Mystery'),
       ('Romance'),
       ('Thriller'),
       ('Horror'),
       ('Historical Fiction'),
       ('Non-Fiction'),
       ('Biography'),
       ('Autobiography');

INSERT INTO books (title, author, editorial_id, available_qty, reserved)
VALUES ('Harry Potter and the Philosopher''s Stone', 'J.K. Rowling', 1, 5, 0),
       ('The Hobbit', 'J.R.R. Tolkien', 1, 3, 0),
       ('The Hunger Games', 'Suzanne Collins', 2, 2, 0),
       ('The Da Vinci Code', 'Dan Brown', 2, 4, 0),
       ('Pride and Prejudice', 'Jane Austen', 3, 1, 0),
       ('G one with the Wind', 'Margaret Mitchell', 3, 3, 0),
       ('Ready Player One', 'Ernest Cline', 4, 5, 0),
       ('Lord of the Flies', 'William Golding', 4, 2, 0),
       ('The Shining', 'Stephen King', 5, 3, 0),
       ('The Diary of Anne Frank', 'Anne Frank', 5, 1, 0);

INSERT INTO books_genres (book_id, genre_id)
VALUES (1, 1),
       (2, 1),
       (3, 2),
       (4, 3),
       (5, 4),
       (6, 7),
       (7, 2),
       (8, 5),
       (9, 6),
       (10, 9);

INSERT INTO users (name, username, password, is_admin)
VALUES ('John Doe', 'john', 'john', 0),
       ('Daniel Cabrera', 'daniel', 'daniel', 1),
       ('Luz Ruiz', 'luz', 'luz', 0),
       ('Franc Rossellò', 'frossell', 'frossell', 1),
       ('Test', 'test', 'test', 1),
       ('user', 'user', 'user', 0);

INSERT INTO rents (user_id, book_id, status)
VALUES (1, 1, 'rented'),
       (2, 2, 'rented'),
       (3, 3, 'rented'),
       (4, 4, 'rented'),
       (5, 5, 'rented');
