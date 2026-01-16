-- Script d'initialisation de la base de données MySQL
-- Restaurant Management System

-- Créer la base de données si elle n'existe pas
CREATE DATABASE IF NOT EXISTS restaurant_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Utiliser la base de données
USE restaurant_db;

-- Créer un utilisateur dédié (optionnel)
CREATE USER IF NOT EXISTS 'restaurant_user'@'localhost' IDENTIFIED BY 'Restaurant@2024';

-- Accorder tous les privilèges sur la base de données
GRANT ALL PRIVILEGES ON restaurant_db.* TO 'restaurant_user'@'localhost';

-- Appliquer les changements
FLUSH PRIVILEGES;

-- Afficher un message de succès
SELECT 'Base de données restaurant_db créée avec succès!' as Message;
