-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Servidor: 127.0.0.1
-- Tiempo de generación: 24-11-2025 a las 05:46:29
-- Versión del servidor: 10.4.32-MariaDB
-- Versión de PHP: 8.0.30

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Base de datos: `apuesta`
--

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `detalles_apuesta`
--

CREATE TABLE `detalles_apuesta` (
  `id_detalle` int(11) NOT NULL,
  `id_ticket` int(11) DEFAULT NULL,
  `id_partido` int(11) DEFAULT NULL,
  `seleccion` varchar(50) DEFAULT NULL,
  `cuota_momento` decimal(5,2) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Volcado de datos para la tabla `detalles_apuesta`
--

INSERT INTO `detalles_apuesta` (`id_detalle`, `id_ticket`, `id_partido`, `seleccion`, `cuota_momento`) VALUES
(1, 1, 101, 'Real Madrid', 2.80),
(2, 1, 102, 'Girona', 6.00),
(3, 2, 101, 'Real Madrid', 2.80),
(4, 2, 102, 'Girona', 6.00),
(5, 3, 101, 'Real Madrid', 2.80),
(6, 4, 101, 'Real Madrid', 2.80),
(7, 4, 102, 'Empate', 4.50),
(8, 5, 101, 'Man. City', 2.50),
(9, 5, 102, 'Girona', 6.00),
(10, 6, 101, 'Real Madrid', 2.80),
(11, 6, 102, 'Barcelona', 1.45),
(12, 7, 101, 'Man. City', 2.50),
(13, 7, 102, 'Girona', 6.00),
(14, 8, 101, 'Real Madrid', 2.80),
(15, 8, 102, 'Barcelona', 1.45),
(16, 9, 101, 'Real Madrid', 2.80),
(17, 9, 102, 'Empate', 4.50),
(18, 9, 105, 'Liverpool', 2.10),
(19, 9, 106, 'AC Milan', 3.00),
(20, 9, 402, 'Rafael Correa', 2.50),
(21, 10, 101, 'Man. City', 2.50),
(22, 10, 102, 'Girona', 6.00),
(23, 11, 101, 'Real Madrid', 2.80),
(24, 11, 102, 'Barcelona', 1.45),
(25, 11, 105, 'Liverpool', 2.10),
(26, 12, 101, 'Man. City', 2.50),
(27, 12, 105, 'Chelsea', 3.20),
(28, 12, 106, 'Empate', 3.20),
(29, 12, 102, 'Girona', 6.00),
(30, 12, 201, 'Lakers', 2.10);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `partidos`
--

CREATE TABLE `partidos` (
  `id` int(11) NOT NULL,
  `categoria` varchar(50) DEFAULT NULL,
  `liga` varchar(100) DEFAULT NULL,
  `local` varchar(100) DEFAULT NULL,
  `img_local` varchar(255) DEFAULT NULL,
  `visitante` varchar(100) DEFAULT NULL,
  `img_visitante` varchar(255) DEFAULT NULL,
  `tiempo` varchar(50) DEFAULT NULL,
  `cuota_1` decimal(5,2) DEFAULT NULL,
  `cuota_x` varchar(20) DEFAULT NULL,
  `cuota_2` decimal(5,2) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Volcado de datos para la tabla `partidos`
--

INSERT INTO `partidos` (`id`, `categoria`, `liga`, `local`, `img_local`, `visitante`, `img_visitante`, `tiempo`, `cuota_1`, `cuota_x`, `cuota_2`) VALUES
(101, 'futbol', 'Champions League', 'Real Madrid', 'madrid.png', 'Man. City', 'city.png', 'LIVE 75\'', 2.80, '3.20', 2.50),
(102, 'futbol', 'La Liga', 'Barcelona', 'barca.png', 'Girona', 'girona.png', '20:00', 1.45, '4.50', 6.00),
(105, 'futbol', 'Premier League', 'Liverpool', 'liverpool.png', 'Chelsea', 'chelsea.png', 'Mañana 10:00', 2.10, '3.60', 3.20),
(106, 'futbol', 'Serie A', 'Juventus', 'juve.png', 'AC Milan', 'milan.png', 'Mañana 14:00', 2.30, '3.20', 3.00),
(201, 'basket', 'NBA', 'Lakers', 'lakers.png', 'Warriors', 'warriors.png', 'LIVE Q3', 2.10, '3,20', 1.90),
(202, 'basket', 'NBA', 'Celtics', 'celtics.png', 'Heat', 'heat.png', 'Hoy 21:00', 1.40, '4.00', 2.80),
(301, 'tenis', 'Roland Garros', 'Alcaraz', 'alcaraz.png', 'Djokovic', 'djokovic.png', 'Set 2 (4-5)', 1.65, '4.50', 2.20),
(401, 'ufc', 'Performance of the Night', 'Ilia Topuria', 'default', 'Charles Oliveira', 'default', 'HOY 23:00', 2.10, '-', 1.90),
(402, 'ufc', 'Performance of the Night', 'Rafael Correa', 'default', 'Álvaro Noboa', 'default', 'HOY 22:00', 2.50, '-', 2.50);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `recarga`
--

CREATE TABLE `recarga` (
  `id_recarga` int(11) NOT NULL,
  `id_usuario` int(11) NOT NULL,
  `monto` decimal(10,2) NOT NULL,
  `metodo` varchar(150) NOT NULL,
  `fecha` datetime NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Volcado de datos para la tabla `recarga`
--

INSERT INTO `recarga` (`id_recarga`, `id_usuario`, `monto`, `metodo`, `fecha`) VALUES
(1, 1, 600.00, 'PayPal', '2025-11-21 22:16:57'),
(2, 1, 10.00, 'Visa/Mastercard', '2025-11-21 22:51:26'),
(3, 1, 10.00, 'Visa/Mastercard', '2025-11-21 23:02:01'),
(4, 5, 5.00, 'Visa/Mastercard', '2025-11-23 19:37:08'),
(5, 1, 40.00, 'Visa/Mastercard', '2025-11-23 20:24:22'),
(6, 9, 100.00, 'Visa/Mastercard', '2025-11-23 22:38:41'),
(7, 5, 5.00, 'Visa/Mastercard', '2025-11-23 23:19:27');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `tickets`
--

CREATE TABLE `tickets` (
  `id_ticket` int(11) NOT NULL,
  `id_usuario` int(11) DEFAULT NULL,
  `monto_total` decimal(10,2) DEFAULT NULL,
  `ganancia_posible` decimal(10,2) DEFAULT NULL,
  `estado` varchar(20) DEFAULT 'pendiente',
  `fecha` datetime DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Volcado de datos para la tabla `tickets`
--

INSERT INTO `tickets` (`id_ticket`, `id_usuario`, `monto_total`, `ganancia_posible`, `estado`, `fecha`) VALUES
(1, 1, 10.00, 168.00, 'pendiente', '2025-11-21 22:27:07'),
(2, 1, 10.00, 168.00, 'pendiente', '2025-11-21 22:41:09'),
(3, 1, 10.00, 28.00, 'pendiente', '2025-11-21 22:43:16'),
(4, 1, 10.00, 126.00, 'pendiente', '2025-11-21 22:48:26'),
(5, 1, 10.00, 150.00, 'pendiente', '2025-11-21 22:51:33'),
(6, 1, 10.00, 40.60, 'pendiente', '2025-11-21 23:02:05'),
(7, 1, 3.00, 45.00, 'pendiente', '2025-11-21 23:45:17'),
(8, 1, 10.00, 40.60, 'pendiente', '2025-11-23 20:23:50'),
(9, 9, 10.00, 1984.50, 'pendiente', '2025-11-23 22:39:02'),
(10, 9, 1.00, 15.00, 'pendiente', '2025-11-23 23:03:43'),
(11, 5, 1.50, 12.79, 'pendiente', '2025-11-23 23:19:45'),
(12, 5, 2.00, 645.12, 'pendiente', '2025-11-23 23:19:56');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `usuarios`
--

CREATE TABLE `usuarios` (
  `id_usuario` int(11) NOT NULL,
  `nombre` varchar(50) NOT NULL,
  `apellido` varchar(50) NOT NULL,
  `email` varchar(100) NOT NULL,
  `contraseña` varchar(225) NOT NULL,
  `fecha_registro` datetime NOT NULL DEFAULT current_timestamp(),
  `saldo` decimal(10,2) NOT NULL,
  `rol` varchar(10) NOT NULL DEFAULT 'user'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Volcado de datos para la tabla `usuarios`
--

INSERT INTO `usuarios` (`id_usuario`, `nombre`, `apellido`, `email`, `contraseña`, `fecha_registro`, `saldo`, `rol`) VALUES
(1, 'Jose', 'angel', 'cr7@gmail.com', '12345', '2025-11-19 22:57:46', 999.00, 'admin'),
(3, 'hhh', 'hh', 'hh@gmail.com', '434', '2025-11-19 22:59:21', 0.00, 'user'),
(5, 'david', 'enrikez', 'davite@gmail.com', '12345', '2025-11-23 18:13:37', 1.50, 'user'),
(9, 'adriana', 'mejia', 'am@gmail.com', '12345', '2025-11-23 22:37:12', 89.00, 'user'),
(10, 'Steven', 'Alcivar', 'sa@gmail.com', '12345', '2025-11-23 22:41:14', 0.00, 'user');

--
-- Índices para tablas volcadas
--

--
-- Indices de la tabla `detalles_apuesta`
--
ALTER TABLE `detalles_apuesta`
  ADD PRIMARY KEY (`id_detalle`),
  ADD KEY `id_ticket` (`id_ticket`),
  ADD KEY `id_partido` (`id_partido`);

--
-- Indices de la tabla `partidos`
--
ALTER TABLE `partidos`
  ADD PRIMARY KEY (`id`);

--
-- Indices de la tabla `recarga`
--
ALTER TABLE `recarga`
  ADD PRIMARY KEY (`id_recarga`),
  ADD KEY `fk_recarga_usuario` (`id_usuario`);

--
-- Indices de la tabla `tickets`
--
ALTER TABLE `tickets`
  ADD PRIMARY KEY (`id_ticket`),
  ADD KEY `id_usuario` (`id_usuario`);

--
-- Indices de la tabla `usuarios`
--
ALTER TABLE `usuarios`
  ADD PRIMARY KEY (`id_usuario`);

--
-- AUTO_INCREMENT de las tablas volcadas
--

--
-- AUTO_INCREMENT de la tabla `detalles_apuesta`
--
ALTER TABLE `detalles_apuesta`
  MODIFY `id_detalle` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=31;

--
-- AUTO_INCREMENT de la tabla `recarga`
--
ALTER TABLE `recarga`
  MODIFY `id_recarga` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=8;

--
-- AUTO_INCREMENT de la tabla `tickets`
--
ALTER TABLE `tickets`
  MODIFY `id_ticket` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=13;

--
-- AUTO_INCREMENT de la tabla `usuarios`
--
ALTER TABLE `usuarios`
  MODIFY `id_usuario` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=11;

--
-- Restricciones para tablas volcadas
--

--
-- Filtros para la tabla `detalles_apuesta`
--
ALTER TABLE `detalles_apuesta`
  ADD CONSTRAINT `detalles_apuesta_ibfk_1` FOREIGN KEY (`id_ticket`) REFERENCES `tickets` (`id_ticket`),
  ADD CONSTRAINT `detalles_apuesta_ibfk_2` FOREIGN KEY (`id_partido`) REFERENCES `partidos` (`id`);

--
-- Filtros para la tabla `recarga`
--
ALTER TABLE `recarga`
  ADD CONSTRAINT `fk_recarga_usuario` FOREIGN KEY (`id_usuario`) REFERENCES `usuarios` (`id_usuario`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- Filtros para la tabla `tickets`
--
ALTER TABLE `tickets`
  ADD CONSTRAINT `tickets_ibfk_1` FOREIGN KEY (`id_usuario`) REFERENCES `usuarios` (`id_usuario`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
