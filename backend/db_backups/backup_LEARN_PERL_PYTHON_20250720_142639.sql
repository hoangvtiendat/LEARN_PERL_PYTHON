-- MySQL dump 10.13  Distrib 5.7.24, for osx11.1 (x86_64)
--
-- Host: localhost    Database: LEARN_PERL_PYTHON
-- ------------------------------------------------------
-- Server version	9.2.0

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `alembic_version`
--

DROP TABLE IF EXISTS `alembic_version`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `alembic_version` (
  `version_num` varchar(32) NOT NULL,
  PRIMARY KEY (`version_num`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `alembic_version`
--

LOCK TABLES `alembic_version` WRITE;
/*!40000 ALTER TABLE `alembic_version` DISABLE KEYS */;
INSERT INTO `alembic_version` VALUES ('59cffd0a6dca');
/*!40000 ALTER TABLE `alembic_version` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `courses`
--

DROP TABLE IF EXISTS `courses`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `courses` (
  `id` int NOT NULL AUTO_INCREMENT,
  `title` varchar(150) NOT NULL,
  `description` text,
  `teacher_id` int NOT NULL,
  `created_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `teacher_id` (`teacher_id`),
  CONSTRAINT `courses_ibfk_1` FOREIGN KEY (`teacher_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `courses`
--

LOCK TABLES `courses` WRITE;
/*!40000 ALTER TABLE `courses` DISABLE KEYS */;
INSERT INTO `courses` VALUES (2,'Lập trình Python cơ bản','Khóa học cho người mới bắt đầu.',2,'2025-07-10 15:48:05');
/*!40000 ALTER TABLE `courses` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `enrollments`
--

DROP TABLE IF EXISTS `enrollments`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `enrollments` (
  `user_id` int NOT NULL,
  `course_id` int NOT NULL,
  `enrolled_at` datetime DEFAULT NULL,
  PRIMARY KEY (`user_id`,`course_id`),
  KEY `course_id` (`course_id`),
  CONSTRAINT `enrollments_ibfk_1` FOREIGN KEY (`course_id`) REFERENCES `courses` (`id`),
  CONSTRAINT `enrollments_ibfk_2` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `enrollments`
--

LOCK TABLES `enrollments` WRITE;
/*!40000 ALTER TABLE `enrollments` DISABLE KEYS */;
/*!40000 ALTER TABLE `enrollments` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `exercises`
--

DROP TABLE IF EXISTS `exercises`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `exercises` (
  `id` int NOT NULL AUTO_INCREMENT,
  `title` varchar(200) NOT NULL,
  `description` text NOT NULL,
  `exercise_type` enum('CODE','MULTIPLE_CHOICE','FILE_UPLOAD') NOT NULL,
  `test_cases` json DEFAULT NULL,
  `lesson_id` int NOT NULL,
  PRIMARY KEY (`id`),
  KEY `lesson_id` (`lesson_id`),
  CONSTRAINT `exercises_ibfk_1` FOREIGN KEY (`lesson_id`) REFERENCES `lessons` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `exercises`
--

LOCK TABLES `exercises` WRITE;
/*!40000 ALTER TABLE `exercises` DISABLE KEYS */;
INSERT INTO `exercises` VALUES (1,'Bài tập cộng 2 số (sửa)','Viết hàm cộng 2 số nguyên (đã cập nhật).','CODE','[{\"input\": [1, 2], \"output\": \"3\"}, {\"input\": [10, 20], \"output\": \"30\"}]',2);
/*!40000 ALTER TABLE `exercises` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `lessons`
--

DROP TABLE IF EXISTS `lessons`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `lessons` (
  `id` int NOT NULL AUTO_INCREMENT,
  `title` varchar(200) NOT NULL,
  `content` text NOT NULL,
  `attachment_url` varchar(300) DEFAULT NULL,
  `order` int NOT NULL,
  `course_id` int NOT NULL,
  PRIMARY KEY (`id`),
  KEY `course_id` (`course_id`),
  CONSTRAINT `lessons_ibfk_1` FOREIGN KEY (`course_id`) REFERENCES `courses` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `lessons`
--

LOCK TABLES `lessons` WRITE;
/*!40000 ALTER TABLE `lessons` DISABLE KEYS */;
INSERT INTO `lessons` VALUES (2,'python1','Introduction Python','youtu.be',1,2);
/*!40000 ALTER TABLE `lessons` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `submissions`
--

DROP TABLE IF EXISTS `submissions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `submissions` (
  `id` int NOT NULL AUTO_INCREMENT,
  `content` text,
  `score` float DEFAULT NULL,
  `feedback` text,
  `status` enum('DRAFT','SUBMITTED','GRADED') NOT NULL,
  `submitted_at` datetime DEFAULT NULL,
  `student_id` int NOT NULL,
  `exercise_id` int NOT NULL,
  PRIMARY KEY (`id`),
  KEY `exercise_id` (`exercise_id`),
  KEY `student_id` (`student_id`),
  CONSTRAINT `submissions_ibfk_1` FOREIGN KEY (`exercise_id`) REFERENCES `exercises` (`id`),
  CONSTRAINT `submissions_ibfk_2` FOREIGN KEY (`student_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `submissions`
--

LOCK TABLES `submissions` WRITE;
/*!40000 ALTER TABLE `submissions` DISABLE KEYS */;
/*!40000 ALTER TABLE `submissions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `token_blocklist`
--

DROP TABLE IF EXISTS `token_blocklist`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `token_blocklist` (
  `id` int NOT NULL AUTO_INCREMENT,
  `jti` varchar(36) NOT NULL,
  `created_at` datetime NOT NULL,
  PRIMARY KEY (`id`),
  KEY `ix_token_blocklist_jti` (`jti`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `token_blocklist`
--

LOCK TABLES `token_blocklist` WRITE;
/*!40000 ALTER TABLE `token_blocklist` DISABLE KEYS */;
INSERT INTO `token_blocklist` VALUES (1,'a8d02e41-49a8-41da-b6e2-c62c81ceb043','2025-07-05 13:08:38'),(2,'25bad16a-6920-4d65-bd9a-84c6c16fbeb1','2025-07-05 13:12:40'),(3,'7c965b34-816c-47ab-84ea-f9a2fedc2a05','2025-07-05 13:13:16'),(4,'bb142a47-629d-4d8e-9dd4-7e1d9efbb3d9','2025-07-05 13:13:39');
/*!40000 ALTER TABLE `token_blocklist` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `user_log`
--

DROP TABLE IF EXISTS `user_log`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `user_log` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int DEFAULT NULL,
  `action` varchar(50) NOT NULL,
  `detail` varchar(255) DEFAULT NULL,
  `timestamp` datetime DEFAULT NULL,
  `username` varchar(120) DEFAULT NULL,
  `email` varchar(120) DEFAULT NULL,
  `full_name` varchar(120) DEFAULT NULL,
  `role` varchar(20) DEFAULT NULL,
  `status` varchar(20) DEFAULT NULL,
  `ip_address` varchar(45) DEFAULT NULL,
  `user_agent` varchar(500) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `user_id` (`user_id`),
  CONSTRAINT `user_log_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `user_log`
--

LOCK TABLES `user_log` WRITE;
/*!40000 ALTER TABLE `user_log` DISABLE KEYS */;
INSERT INTO `user_log` VALUES (1,2,'login','Đăng nhập thành công','2025-07-20 06:32:50',NULL,NULL,NULL,NULL,NULL,NULL,NULL),(2,2,'login','Đăng nhập thành công','2025-07-20 06:37:13',NULL,NULL,NULL,NULL,NULL,NULL,NULL),(3,2,'login','Đăng nhập thành công','2025-07-20 07:26:30',NULL,NULL,NULL,NULL,NULL,NULL,NULL);
/*!40000 ALTER TABLE `user_log` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `users` (
  `id` int NOT NULL AUTO_INCREMENT,
  `email` varchar(120) NOT NULL,
  `full_name` varchar(120) NOT NULL,
  `password_hash` varchar(256) NOT NULL,
  `role` enum('STUDENT','TEACHER','ADMIN') NOT NULL,
  `two_fa_enabled` tinyint(1) DEFAULT NULL,
  `two_fa_secret` varchar(255) DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  `updated_at` datetime DEFAULT NULL,
  `student_code` varchar(20) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `ix_users_email` (`email`),
  UNIQUE KEY `ix_users_student_code` (`student_code`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users`
--

LOCK TABLES `users` WRITE;
/*!40000 ALTER TABLE `users` DISABLE KEYS */;
INSERT INTO `users` VALUES (1,'newstudent@example.com','Trần Thị B','scrypt:32768:8:1$YzILbDDWyKq901LW$32eebf9c4c6eb96cdab847a2b24e9cbfb5d25a23724e80c5a3e1dbedc455d2fc3903dc6b6bd8de21ba17c055ab60edaa7efee64211f70dfc3fa9b5d0986c7c0f','STUDENT',0,NULL,'2025-07-02 04:59:36','2025-07-02 04:59:36','222'),(2,'hngvtdat010@gmail.com','Đạt Hoàng Văn Tiêns','scrypt:32768:8:1$eIkUUps74D4z6Qjb$83597130445bdf1246fc2ace6ef709604783b997ff11fd96e93b72db3c463d7a757de152e3cac9d8f6ecb730fbcd33700152b850bb98d39e40e13d600546884f','ADMIN',0,NULL,'2025-07-02 05:03:09','2025-07-10 15:54:06','111'),(3,'hoangvantiendat.9b2018@gmail.com','Hoang Van Tien Dat','scrypt:32768:8:1$qHcotTknnjb6LTcD$525ed504244ef1b128155c45ab58a90167f3aef20d6f0e4fd46d7dcbc3ea58bb4a5c7ff96d9baf56e715f4b19faccd902250ee84e232e88283756560ea9f8436','STUDENT',0,NULL,'2025-07-03 16:30:40','2025-07-05 11:38:03','333'),(5,'hoangvantienda.9b2018@gmail.com','Hoang Van Tien Dat','scrypt:32768:8:1$Ixk4YuU21xQuNwp0$517197ecfc4621576296b957d81e9d164db641bc25eb504f7dfe9e2c349dda67512fb89d3340c821d3e4944b44d48510cef674242a1fed856025e9ba08ee08c0','STUDENT',0,NULL,'2025-07-04 18:54:04','2025-07-04 18:54:04','123456');
/*!40000 ALTER TABLE `users` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-07-20 14:26:39
