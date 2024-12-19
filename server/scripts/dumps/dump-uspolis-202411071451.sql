--
-- PostgreSQL database dump
--

-- Dumped from database version 12.19 (Ubuntu 12.19-0ubuntu0.20.04.1)
-- Dumped by pg_dump version 16.3

-- Started on 2024-11-07 14:51:59 -03

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- TOC entry 6 (class 2615 OID 2200)
-- Name: public; Type: SCHEMA; Schema: -; Owner: postgres
--

CREATE SCHEMA public;


ALTER SCHEMA public OWNER TO postgres;

--
-- TOC entry 3239 (class 0 OID 0)
-- Dependencies: 6
-- Name: SCHEMA public; Type: COMMENT; Schema: -; Owner: postgres
--

COMMENT ON SCHEMA public IS 'standard public schema';


--
-- TOC entry 692 (class 1247 OID 25049)
-- Name: classtype; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.classtype AS ENUM (
    'PRACTIC',
    'THEORIC',
    'VINCULATED_THEORIC',
    'VINCULATED_PRACTIC'
);


ALTER TYPE public.classtype OWNER TO postgres;

--
-- TOC entry 745 (class 1247 OID 25296)
-- Name: monthweek; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.monthweek AS ENUM (
    'FIRST',
    'SECOND',
    'THIRD',
    'LAST'
);


ALTER TYPE public.monthweek OWNER TO postgres;

--
-- TOC entry 742 (class 1247 OID 25282)
-- Name: recurrence; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.recurrence AS ENUM (
    'DAILY',
    'WEEKLY',
    'BIWEEKLY',
    'MONTHLY',
    'NONE',
    'CUSTOM'
);


ALTER TYPE public.recurrence OWNER TO postgres;

--
-- TOC entry 731 (class 1247 OID 25232)
-- Name: reservationtype; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.reservationtype AS ENUM (
    'EXAM',
    'MEETING',
    'EVENT',
    'OTHER'
);


ALTER TYPE public.reservationtype OWNER TO postgres;

--
-- TOC entry 669 (class 1247 OID 24978)
-- Name: subjecttype; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.subjecttype AS ENUM (
    'BIANNUAL',
    'FOUR_MONTHLY',
    'OTHER'
);


ALTER TYPE public.subjecttype OWNER TO postgres;

--
-- TOC entry 739 (class 1247 OID 25266)
-- Name: weekday; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.weekday AS ENUM (
    'MONDAY',
    'TUESDAY',
    'WEDNESDAY',
    'THURSDAY',
    'FRIDAY',
    'SATURDAY',
    'SUNDAY'
);


ALTER TYPE public.weekday OWNER TO postgres;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- TOC entry 202 (class 1259 OID 24950)
-- Name: alembic_version; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.alembic_version (
    version_num character varying(32) NOT NULL
);


ALTER TABLE public.alembic_version OWNER TO postgres;

--
-- TOC entry 212 (class 1259 OID 25016)
-- Name: building; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.building (
    id integer NOT NULL,
    name character varying NOT NULL,
    created_by_id integer,
    updated_at timestamp without time zone NOT NULL
);


ALTER TABLE public.building OWNER TO postgres;

--
-- TOC entry 211 (class 1259 OID 25014)
-- Name: building_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.building_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.building_id_seq OWNER TO postgres;

--
-- TOC entry 3241 (class 0 OID 0)
-- Dependencies: 211
-- Name: building_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.building_id_seq OWNED BY public.building.id;


--
-- TOC entry 214 (class 1259 OID 25033)
-- Name: calendar; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.calendar (
    id integer NOT NULL,
    name character varying NOT NULL,
    created_by_id integer
);


ALTER TABLE public.calendar OWNER TO postgres;

--
-- TOC entry 213 (class 1259 OID 25031)
-- Name: calendar_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.calendar_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.calendar_id_seq OWNER TO postgres;

--
-- TOC entry 3242 (class 0 OID 0)
-- Dependencies: 213
-- Name: calendar_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.calendar_id_seq OWNED BY public.calendar.id;


--
-- TOC entry 221 (class 1259 OID 25109)
-- Name: calendarholidaycategorylink; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.calendarholidaycategorylink (
    calendar_id integer NOT NULL,
    holiday_category_id integer NOT NULL
);


ALTER TABLE public.calendarholidaycategorylink OWNER TO postgres;

--
-- TOC entry 216 (class 1259 OID 25059)
-- Name: class; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.class (
    id integer NOT NULL,
    start_date date NOT NULL,
    end_date date NOT NULL,
    code character varying NOT NULL,
    professors character varying[],
    type public.classtype NOT NULL,
    vacancies integer NOT NULL,
    subscribers integer NOT NULL,
    pendings integer NOT NULL,
    air_conditionating boolean NOT NULL,
    accessibility boolean NOT NULL,
    projector boolean NOT NULL,
    ignore_to_allocate boolean NOT NULL,
    full_allocated boolean NOT NULL,
    updated_at timestamp without time zone NOT NULL,
    subject_id integer NOT NULL
);


ALTER TABLE public.class OWNER TO postgres;

--
-- TOC entry 215 (class 1259 OID 25057)
-- Name: class_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.class_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.class_id_seq OWNER TO postgres;

--
-- TOC entry 3243 (class 0 OID 0)
-- Dependencies: 215
-- Name: class_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.class_id_seq OWNED BY public.class.id;


--
-- TOC entry 222 (class 1259 OID 25124)
-- Name: classcalendarlink; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.classcalendarlink (
    class_id integer NOT NULL,
    calendar_id integer NOT NULL
);


ALTER TABLE public.classcalendarlink OWNER TO postgres;

--
-- TOC entry 224 (class 1259 OID 25141)
-- Name: classroom; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.classroom (
    name character varying NOT NULL,
    capacity integer NOT NULL,
    floor integer NOT NULL,
    ignore_to_allocate boolean NOT NULL,
    accessibility boolean NOT NULL,
    projector boolean NOT NULL,
    air_conditioning boolean NOT NULL,
    updated_at timestamp without time zone NOT NULL,
    created_by_id integer NOT NULL,
    building_id integer NOT NULL,
    id integer NOT NULL
);


ALTER TABLE public.classroom OWNER TO postgres;

--
-- TOC entry 223 (class 1259 OID 25139)
-- Name: classroom_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.classroom_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.classroom_id_seq OWNER TO postgres;

--
-- TOC entry 3244 (class 0 OID 0)
-- Dependencies: 223
-- Name: classroom_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.classroom_id_seq OWNED BY public.classroom.id;


--
-- TOC entry 218 (class 1259 OID 25078)
-- Name: comment; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.comment (
    id integer NOT NULL,
    comment character varying NOT NULL,
    email character varying,
    created_by_id integer,
    created_at timestamp without time zone NOT NULL
);


ALTER TABLE public.comment OWNER TO postgres;

--
-- TOC entry 217 (class 1259 OID 25076)
-- Name: comment_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.comment_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.comment_id_seq OWNER TO postgres;

--
-- TOC entry 3245 (class 0 OID 0)
-- Dependencies: 217
-- Name: comment_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.comment_id_seq OWNED BY public.comment.id;


--
-- TOC entry 236 (class 1259 OID 25362)
-- Name: forumpost; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.forumpost (
    id integer NOT NULL,
    class_id integer NOT NULL,
    subject_id integer NOT NULL,
    content character varying,
    user_id integer NOT NULL,
    created_at timestamp without time zone NOT NULL,
    report_count integer NOT NULL,
    reply_of_post_id integer,
    replies_count integer NOT NULL,
    enabled boolean
);


ALTER TABLE public.forumpost OWNER TO postgres;

--
-- TOC entry 235 (class 1259 OID 25360)
-- Name: forumpost_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.forumpost_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.forumpost_id_seq OWNER TO postgres;

--
-- TOC entry 3246 (class 0 OID 0)
-- Dependencies: 235
-- Name: forumpost_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.forumpost_id_seq OWNED BY public.forumpost.id;


--
-- TOC entry 237 (class 1259 OID 33142)
-- Name: forumpostreportlink; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.forumpostreportlink (
    forum_post_id integer NOT NULL,
    mobile_user_id integer NOT NULL
);


ALTER TABLE public.forumpostreportlink OWNER TO postgres;

--
-- TOC entry 226 (class 1259 OID 25185)
-- Name: holiday; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.holiday (
    id integer NOT NULL,
    date date NOT NULL,
    updated_at timestamp without time zone NOT NULL,
    category_id integer NOT NULL,
    created_by_id integer NOT NULL,
    name character varying NOT NULL
);


ALTER TABLE public.holiday OWNER TO postgres;

--
-- TOC entry 225 (class 1259 OID 25183)
-- Name: holiday_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.holiday_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.holiday_id_seq OWNER TO postgres;

--
-- TOC entry 3247 (class 0 OID 0)
-- Dependencies: 225
-- Name: holiday_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.holiday_id_seq OWNED BY public.holiday.id;


--
-- TOC entry 220 (class 1259 OID 25094)
-- Name: holidaycategory; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.holidaycategory (
    id integer NOT NULL,
    name character varying NOT NULL,
    created_by_id integer NOT NULL
);


ALTER TABLE public.holidaycategory OWNER TO postgres;

--
-- TOC entry 219 (class 1259 OID 25092)
-- Name: holidaycategory_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.holidaycategory_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.holidaycategory_id_seq OWNER TO postgres;

--
-- TOC entry 3248 (class 0 OID 0)
-- Dependencies: 219
-- Name: holidaycategory_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.holidaycategory_id_seq OWNED BY public.holidaycategory.id;


--
-- TOC entry 204 (class 1259 OID 24957)
-- Name: institutionalevent; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.institutionalevent (
    id integer NOT NULL,
    title character varying NOT NULL,
    description character varying NOT NULL,
    category character varying NOT NULL,
    start timestamp without time zone NOT NULL,
    "end" timestamp without time zone NOT NULL,
    location character varying,
    building character varying,
    classroom character varying,
    external_link character varying,
    likes integer NOT NULL,
    created_at timestamp without time zone NOT NULL
);


ALTER TABLE public.institutionalevent OWNER TO postgres;

--
-- TOC entry 203 (class 1259 OID 24955)
-- Name: institutionalevent_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.institutionalevent_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.institutionalevent_id_seq OWNER TO postgres;

--
-- TOC entry 3249 (class 0 OID 0)
-- Dependencies: 203
-- Name: institutionalevent_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.institutionalevent_id_seq OWNED BY public.institutionalevent.id;


--
-- TOC entry 206 (class 1259 OID 24968)
-- Name: mobileuser; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.mobileuser (
    id integer NOT NULL,
    sub character varying NOT NULL,
    email character varying NOT NULL,
    given_name character varying NOT NULL,
    family_name character varying NOT NULL,
    picture_url character varying
);


ALTER TABLE public.mobileuser OWNER TO postgres;

--
-- TOC entry 205 (class 1259 OID 24966)
-- Name: mobileuser_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.mobileuser_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.mobileuser_id_seq OWNER TO postgres;

--
-- TOC entry 3250 (class 0 OID 0)
-- Dependencies: 205
-- Name: mobileuser_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.mobileuser_id_seq OWNED BY public.mobileuser.id;


--
-- TOC entry 234 (class 1259 OID 25330)
-- Name: occurrence; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.occurrence (
    id integer NOT NULL,
    start_time time without time zone NOT NULL,
    end_time time without time zone NOT NULL,
    date date NOT NULL,
    classroom_id integer,
    schedule_id integer
);


ALTER TABLE public.occurrence OWNER TO postgres;

--
-- TOC entry 233 (class 1259 OID 25328)
-- Name: occurrence_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.occurrence_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.occurrence_id_seq OWNER TO postgres;

--
-- TOC entry 3251 (class 0 OID 0)
-- Dependencies: 233
-- Name: occurrence_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.occurrence_id_seq OWNED BY public.occurrence.id;


--
-- TOC entry 230 (class 1259 OID 25243)
-- Name: reservation; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.reservation (
    id integer NOT NULL,
    name character varying NOT NULL,
    type public.reservationtype NOT NULL,
    description character varying,
    updated_at timestamp without time zone NOT NULL,
    classroom_id integer NOT NULL,
    created_by_id integer NOT NULL
);


ALTER TABLE public.reservation OWNER TO postgres;

--
-- TOC entry 229 (class 1259 OID 25241)
-- Name: reservation_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.reservation_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.reservation_id_seq OWNER TO postgres;

--
-- TOC entry 3252 (class 0 OID 0)
-- Dependencies: 229
-- Name: reservation_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.reservation_id_seq OWNED BY public.reservation.id;


--
-- TOC entry 232 (class 1259 OID 25307)
-- Name: schedule; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.schedule (
    id integer NOT NULL,
    start_date date NOT NULL,
    end_date date NOT NULL,
    start_time time without time zone NOT NULL,
    end_time time without time zone NOT NULL,
    week_day public.weekday,
    allocated boolean NOT NULL,
    recurrence public.recurrence NOT NULL,
    month_week public.monthweek,
    all_day boolean NOT NULL,
    class_id integer,
    classroom_id integer,
    reservation_id integer
);


ALTER TABLE public.schedule OWNER TO postgres;

--
-- TOC entry 231 (class 1259 OID 25305)
-- Name: schedule_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.schedule_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.schedule_id_seq OWNER TO postgres;

--
-- TOC entry 3253 (class 0 OID 0)
-- Dependencies: 231
-- Name: schedule_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.schedule_id_seq OWNED BY public.schedule.id;


--
-- TOC entry 208 (class 1259 OID 24987)
-- Name: subject; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.subject (
    id integer NOT NULL,
    name character varying NOT NULL,
    code character varying NOT NULL,
    professors character varying[] NOT NULL,
    type public.subjecttype,
    class_credit integer NOT NULL,
    work_credit integer NOT NULL,
    activation date NOT NULL,
    deactivation date
);


ALTER TABLE public.subject OWNER TO postgres;

--
-- TOC entry 207 (class 1259 OID 24985)
-- Name: subject_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.subject_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.subject_id_seq OWNER TO postgres;

--
-- TOC entry 3254 (class 0 OID 0)
-- Dependencies: 207
-- Name: subject_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.subject_id_seq OWNED BY public.subject.id;


--
-- TOC entry 227 (class 1259 OID 25201)
-- Name: subjectbuildinglink; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.subjectbuildinglink (
    subject_id integer NOT NULL,
    building_id integer NOT NULL
);


ALTER TABLE public.subjectbuildinglink OWNER TO postgres;

--
-- TOC entry 210 (class 1259 OID 24999)
-- Name: user; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public."user" (
    id integer NOT NULL,
    username character varying NOT NULL,
    email character varying NOT NULL,
    is_admin boolean NOT NULL,
    name character varying NOT NULL,
    cognito_id character varying NOT NULL,
    updated_at timestamp without time zone NOT NULL,
    created_by_id integer
);


ALTER TABLE public."user" OWNER TO postgres;

--
-- TOC entry 209 (class 1259 OID 24997)
-- Name: user_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.user_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.user_id_seq OWNER TO postgres;

--
-- TOC entry 3255 (class 0 OID 0)
-- Dependencies: 209
-- Name: user_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.user_id_seq OWNED BY public."user".id;


--
-- TOC entry 228 (class 1259 OID 25216)
-- Name: userbuildinglink; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.userbuildinglink (
    user_id integer NOT NULL,
    building_id integer NOT NULL
);


ALTER TABLE public.userbuildinglink OWNER TO postgres;

--
-- TOC entry 2973 (class 2604 OID 25019)
-- Name: building id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.building ALTER COLUMN id SET DEFAULT nextval('public.building_id_seq'::regclass);


--
-- TOC entry 2974 (class 2604 OID 25036)
-- Name: calendar id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.calendar ALTER COLUMN id SET DEFAULT nextval('public.calendar_id_seq'::regclass);


--
-- TOC entry 2975 (class 2604 OID 25062)
-- Name: class id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.class ALTER COLUMN id SET DEFAULT nextval('public.class_id_seq'::regclass);


--
-- TOC entry 2978 (class 2604 OID 25144)
-- Name: classroom id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.classroom ALTER COLUMN id SET DEFAULT nextval('public.classroom_id_seq'::regclass);


--
-- TOC entry 2976 (class 2604 OID 25081)
-- Name: comment id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.comment ALTER COLUMN id SET DEFAULT nextval('public.comment_id_seq'::regclass);


--
-- TOC entry 2983 (class 2604 OID 25365)
-- Name: forumpost id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.forumpost ALTER COLUMN id SET DEFAULT nextval('public.forumpost_id_seq'::regclass);


--
-- TOC entry 2979 (class 2604 OID 25188)
-- Name: holiday id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.holiday ALTER COLUMN id SET DEFAULT nextval('public.holiday_id_seq'::regclass);


--
-- TOC entry 2977 (class 2604 OID 25097)
-- Name: holidaycategory id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.holidaycategory ALTER COLUMN id SET DEFAULT nextval('public.holidaycategory_id_seq'::regclass);


--
-- TOC entry 2969 (class 2604 OID 24960)
-- Name: institutionalevent id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.institutionalevent ALTER COLUMN id SET DEFAULT nextval('public.institutionalevent_id_seq'::regclass);


--
-- TOC entry 2970 (class 2604 OID 24971)
-- Name: mobileuser id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.mobileuser ALTER COLUMN id SET DEFAULT nextval('public.mobileuser_id_seq'::regclass);


--
-- TOC entry 2982 (class 2604 OID 25333)
-- Name: occurrence id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.occurrence ALTER COLUMN id SET DEFAULT nextval('public.occurrence_id_seq'::regclass);


--
-- TOC entry 2980 (class 2604 OID 25246)
-- Name: reservation id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.reservation ALTER COLUMN id SET DEFAULT nextval('public.reservation_id_seq'::regclass);


--
-- TOC entry 2981 (class 2604 OID 25310)
-- Name: schedule id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.schedule ALTER COLUMN id SET DEFAULT nextval('public.schedule_id_seq'::regclass);


--
-- TOC entry 2971 (class 2604 OID 24990)
-- Name: subject id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.subject ALTER COLUMN id SET DEFAULT nextval('public.subject_id_seq'::regclass);


--
-- TOC entry 2972 (class 2604 OID 25354)
-- Name: user id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."user" ALTER COLUMN id SET DEFAULT nextval('public.user_id_seq'::regclass);


--
-- TOC entry 3198 (class 0 OID 24950)
-- Dependencies: 202
-- Data for Name: alembic_version; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.alembic_version (version_num) FROM stdin;
5fc1e85f84a3
\.


--
-- TOC entry 3208 (class 0 OID 25016)
-- Dependencies: 212
-- Data for Name: building; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.building (id, name, created_by_id, updated_at) FROM stdin;
2   Elétrica	5	2024-07-31 22:04:12.333536
3	Produção	5	2024-07-31 22:04:12.333536
4	Civil	5	2024-07-31 22:04:12.333536
1	Biênio	2	2024-07-31 22:04:12.333536
5	Metalúrgica	5	2024-07-31 22:04:12.333536
6	Mecânica	5	2024-07-31 22:04:12.333536
7	Química	5	2024-08-02 19:15:49.519259
8	Minas e Petróleo	5	2024-08-02 19:15:49.519259
\.


--
-- TOC entry 3210 (class 0 OID 25033)
-- Dependencies: 214
-- Data for Name: calendar; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.calendar (id, name, created_by_id) FROM stdin;
1	USP	5
\.


--
-- TOC entry 3217 (class 0 OID 25109)
-- Dependencies: 221
-- Data for Name: calendarholidaycategorylink; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.calendarholidaycategorylink (calendar_id, holiday_category_id) FROM stdin;
1	1
\.


--
-- TOC entry 3212 (class 0 OID 25059)
-- Dependencies: 216
-- Data for Name: class; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.class (id, start_date, end_date, code, professors, type, vacancies, subscribers, pendings, air_conditionating, accessibility, projector, ignore_to_allocate, full_allocated, updated_at, subject_id) FROM stdin;
1	2024-08-05	2024-12-12	2024201	{"Juan Carlos Cebrian Amasifen"}	THEORIC	79	82	2	f	f	f	f	f	2024-07-31 22:04:12.434428	1
2	2024-08-05	2024-12-12	2024201	{"Silvio Giuseppe Di Santo"}	VINCULATED_PRACTIC	21	20	1	f	f	f	f	f	2024-07-31 22:04:12.434428	2
3	2024-08-05	2024-12-12	2024202	{"Silvio Giuseppe Di Santo"}	VINCULATED_PRACTIC	20	12	0	f	f	f	f	f	2024-07-31 22:04:12.434428	2
4	2024-08-05	2024-12-12	2024203	{"Carlos Frederico Meschini Almeida"}	VINCULATED_PRACTIC	20	20	0	f	f	f	f	f	2024-07-31 22:04:12.434428	2
5	2024-08-05	2024-12-12	2024204	{"Carlos Frederico Meschini Almeida"}	VINCULATED_PRACTIC	22	22	0	f	f	f	f	f	2024-07-31 22:04:12.434428	2
6	2024-08-05	2024-12-12	2024250	{"Josemir Coelho Santos"}	VINCULATED_THEORIC	83	74	1	f	f	f	f	f	2024-07-31 22:04:12.434428	2
7	2024-08-05	2024-12-12	2024201	{"Maurício Barbosa de Camargo Salles"}	THEORIC	72	51	16	f	f	f	f	f	2024-07-31 22:04:12.434428	3
8	2024-08-05	2024-12-12	2024201	{"Silvio Giuseppe Di Santo"}	THEORIC	83	71	0	f	f	f	f	f	2024-07-31 22:04:12.434428	4
9	2024-05-06	2024-08-16	2024201	{"Carlos Frederico Meschini Almeida"}	VINCULATED_PRACTIC	17	13	0	f	f	f	f	f	2024-07-31 22:04:12.434428	5
10	2024-05-06	2024-08-16	2024202	{"Carlos Frederico Meschini Almeida"}	VINCULATED_PRACTIC	22	11	0	f	f	f	f	f	2024-07-31 22:04:12.434428	5
11	2024-05-06	2024-08-16	2024203	{"(R) Milana Lima dos Santos"}	VINCULATED_PRACTIC	16	13	0	f	f	f	f	f	2024-07-31 22:04:12.434428	5
12	2024-05-06	2024-08-16	2024204	{"(R) Milana Lima dos Santos"}	VINCULATED_PRACTIC	16	14	0	f	f	f	f	f	2024-07-31 22:04:12.434428	5
13	2024-05-06	2024-08-16	2024250	{"(R) Milana Lima dos Santos"}	VINCULATED_THEORIC	65	51	0	f	f	f	f	f	2024-07-31 22:04:12.434428	5
14	2024-08-05	2024-12-12	2024290	{"(R) Josemir Coelho Santos"}	THEORIC	35	0	0	f	f	f	f	f	2024-07-31 22:04:12.434428	6
15	2024-08-05	2024-12-12	2024201	{"Milana Lima dos Santos"}	PRACTIC	20	20	0	f	f	f	f	f	2024-07-31 22:04:12.434428	7
16	2024-08-05	2024-12-12	2024202	{"Milana Lima dos Santos"}	PRACTIC	20	12	0	f	f	f	f	f	2024-07-31 22:04:12.434428	7
17	2024-08-05	2024-12-12	2024203	{"Renato Machado Monaro"}	PRACTIC	21	20	0	f	f	f	f	f	2024-07-31 22:04:12.434428	7
18	2024-08-05	2024-12-12	2024204	{"Renato Machado Monaro"}	PRACTIC	20	20	0	f	f	f	f	f	2024-07-31 22:04:12.434428	7
19	2024-08-05	2024-12-12	2024201	{"(R) Giovanni Manassero Junior"}	THEORIC	95	126	0	f	f	f	f	f	2024-07-31 22:04:12.434428	8
20	2024-08-05	2024-12-12	2024201	{"Carlos Eduardo de Morais Pereira"}	VINCULATED_PRACTIC	19	18	0	f	f	f	f	f	2024-07-31 22:04:12.434428	9
21	2024-08-05	2024-12-12	2024202	{"Carlos Eduardo de Morais Pereira"}	VINCULATED_PRACTIC	19	26	1	f	f	f	f	f	2024-07-31 22:04:12.434428	9
22	2024-08-05	2024-12-12	2024203	{"(R) Milana Lima dos Santos"}	VINCULATED_PRACTIC	19	20	1	f	f	f	f	f	2024-07-31 22:04:12.434428	9
23	2024-08-05	2024-12-12	2024204	{"(R) Milana Lima dos Santos"}	VINCULATED_PRACTIC	18	20	0	f	f	f	f	f	2024-07-31 22:04:12.434428	9
24	2024-08-05	2024-12-12	2024250	{"(R) Milana Lima dos Santos"}	VINCULATED_THEORIC	85	84	2	f	f	f	f	f	2024-07-31 22:04:12.434428	9
25	2024-08-05	2024-12-12	2024201	{"Sérgio Luiz Pereira"}	PRACTIC	20	14	0	f	f	f	f	f	2024-07-31 22:04:12.434428	10
26	2024-08-05	2024-12-12	2024202	{"Sérgio Luiz Pereira"}	PRACTIC	20	2	0	f	f	f	f	f	2024-07-31 22:04:12.434428	10
27	2024-08-05	2024-12-12	2024203	{"Maurício Barbosa de Camargo Salles"}	PRACTIC	22	20	0	f	f	f	f	f	2024-07-31 22:04:12.434428	10
28	2024-08-05	2024-12-12	2024201	{"(R) Silvio Ikuyo Nabeta"}	PRACTIC	15	15	0	f	f	f	f	f	2024-07-31 22:04:12.434428	11
29	2024-08-05	2024-12-12	2024202	{"(R) Silvio Ikuyo Nabeta"}	PRACTIC	18	7	0	f	f	f	f	f	2024-07-31 22:04:12.434428	11
30	2024-08-05	2024-12-12	2024201	{"Carlos Frederico Meschini Almeida"}	PRACTIC	16	9	0	f	f	f	f	f	2024-07-31 22:04:12.434428	12
31	2024-08-05	2024-12-12	2024202	{"Carlos Frederico Meschini Almeida"}	PRACTIC	15	15	0	f	f	f	f	f	2024-07-31 22:04:12.434428	12
32	2024-08-05	2024-12-12	2024201	{"(R) Ivan Eduardo Chabu"}	THEORIC	46	25	1	f	f	f	f	f	2024-07-31 22:04:12.434428	13
33	2024-08-05	2024-12-12	2024201	{"(R) Nelson Kagan"}	THEORIC	61	21	1	f	f	f	f	f	2024-07-31 22:04:12.434428	14
34	2024-08-05	2024-12-12	2024201	{"(R) Eduardo Lorenzetti Pellini","(R) Milana Lima dos Santos"}	PRACTIC	18	14	1	f	f	f	f	f	2024-07-31 22:04:12.434428	15
35	2024-08-05	2024-12-12	2024202	{"(R) Eduardo Lorenzetti Pellini","(R) Milana Lima dos Santos"}	PRACTIC	18	14	0	f	f	f	f	f	2024-07-31 22:04:12.434428	15
36	2024-08-05	2024-12-12	2024201	{"(R) Giovanni Manassero Junior"}	THEORIC	55	2	0	f	f	f	f	f	2024-07-31 22:04:12.434428	16
37	2024-08-05	2024-12-12	2024201	{"(R) Jose Aquiles Baesso Grimoni","André Luiz Veiga Gimenes"}	PRACTIC	18	15	1	f	f	f	f	f	2024-07-31 22:04:12.434428	17
38	2024-08-05	2024-12-12	2024202	{"(R) Jose Aquiles Baesso Grimoni","André Luiz Veiga Gimenes"}	PRACTIC	18	16	1	f	f	f	f	f	2024-07-31 22:04:12.434428	17
39	2024-08-05	2024-12-12	2024201	{"(R) André Luiz Veiga Gimenes"}	THEORIC	66	42	4	f	f	f	f	f	2024-07-31 22:04:12.434428	18
40	2024-08-05	2024-12-12	2024201	{"(R) Lourenço Matakas Junior","(R) Wilson Komatsu"}	VINCULATED_PRACTIC	16	13	1	f	f	f	f	f	2024-07-31 22:04:12.434428	19
41	2024-08-05	2024-12-12	2024202	{"(R) Lourenço Matakas Junior","(R) Wilson Komatsu"}	VINCULATED_PRACTIC	17	7	0	f	f	f	f	f	2024-07-31 22:04:12.434428	19
42	2024-08-05	2024-12-12	2024203	{"(R) Lourenço Matakas Junior","(R) Wilson Komatsu"}	VINCULATED_PRACTIC	17	9	0	f	f	f	f	f	2024-07-31 22:04:12.434428	19
43	2024-08-05	2024-12-12	2024250	{"(R) Lourenço Matakas Junior","(R) Wilson Komatsu"}	VINCULATED_THEORIC	62	29	1	f	f	f	f	f	2024-07-31 22:04:12.434428	19
44	2024-08-05	2024-12-12	2024201	{"(R) Lourenço Matakas Junior"}	THEORIC	40	4	1	f	f	f	f	f	2024-07-31 22:04:12.434428	20
45	2024-08-05	2024-12-12	2024201	{"(R) Silvio Giuseppe Di Santo"}	THEORIC	40	9	0	f	f	f	f	f	2024-07-31 22:04:12.434428	21
46	2024-08-05	2024-12-12	2024202	{"Luiz Claudio Ribeiro Galvão"}	THEORIC	40	3	0	f	f	f	f	f	2024-07-31 22:04:12.434428	21
47	2024-08-05	2024-12-12	2024203	{"Marco Antonio Saidel"}	THEORIC	40	3	0	f	f	f	f	f	2024-07-31 22:04:12.434428	21
48	2024-08-05	2024-12-12	2024204	{"(R) Dorel Soares Ramos"}	THEORIC	40	5	0	f	f	f	f	f	2024-07-31 22:04:12.434428	21
49	2024-08-05	2024-12-12	2024205	{"(R) Giovanni Manassero Junior"}	THEORIC	20	3	0	f	f	f	f	f	2024-07-31 22:04:12.434428	21
50	2024-08-05	2024-12-12	2024201	{"(R) Milana Lima dos Santos"}	PRACTIC	15	6	1	f	f	f	f	f	2024-07-31 22:04:12.434428	22
51	2024-08-05	2024-12-12	2024201	{"(R) Ivan Eduardo Chabu"}	THEORIC	60	10	0	f	f	f	f	f	2024-07-31 22:04:12.434428	23
52	2024-08-05	2024-12-12	2024201	{"(R) Wilson Komatsu"}	THEORIC	50	11	0	f	f	f	f	f	2024-07-31 22:04:12.434428	24
53	2024-08-05	2024-12-12	2024201	{"(R) Luiz Cezar Trintinalia"}	THEORIC	84	75	4	f	f	f	f	f	2024-07-31 22:04:12.434428	25
54	2024-08-05	2024-12-12	2024202	{"(R) Luiz Lebensztajn"}	THEORIC	80	68	4	f	f	f	f	f	2024-07-31 22:04:12.434428	25
55	2024-08-05	2024-12-12	2024203	{"Murilo Hiroaki Seko"}	THEORIC	80	56	3	f	f	f	f	f	2024-07-31 22:04:12.434428	25
56	2024-08-05	2024-12-12	2024201	{"Renata Valeri de Freitas"}	THEORIC	75	63	4	f	f	f	f	f	2024-07-31 22:04:12.434428	26
57	2024-08-05	2024-12-12	2024202	{"(R) Luiz Cezar Trintinalia"}	THEORIC	75	66	3	f	f	f	f	f	2024-07-31 22:04:12.434428	26
58	2024-08-05	2024-12-12	2024203	{"Juan Luis Poletti Soto"}	THEORIC	75	56	0	f	f	f	f	f	2024-07-31 22:04:12.434428	26
59	2024-08-05	2024-12-12	2024201	{"(R) Marcio Eisencraft"}	THEORIC	70	70	3	f	f	f	f	f	2024-07-31 22:04:12.434428	27
60	2024-08-05	2024-12-12	2024202	{"(R) Cristiano Magalhaes Panazio"}	THEORIC	70	70	6	f	f	f	f	f	2024-07-31 22:04:12.434428	27
61	2024-08-05	2024-12-12	2024203	{""}	THEORIC	70	66	6	f	f	f	f	f	2024-07-31 22:04:12.434428	27
62	2024-08-05	2024-12-12	2024201	{"Renata Valeri de Freitas"}	THEORIC	83	75	9	f	f	f	f	f	2024-07-31 22:04:12.434428	28
63	2024-08-05	2024-12-12	2024202	{"Henrique Takachi Moriya"}	THEORIC	80	71	2	f	f	f	f	f	2024-07-31 22:04:12.434428	28
64	2024-08-05	2024-12-12	2024203	{""}	THEORIC	80	41	2	f	f	f	f	f	2024-07-31 22:04:12.434428	28
65	2024-08-05	2024-12-12	2024250	{"Murilo Hiroaki Seko"}	PRACTIC	10	14	0	f	f	f	f	f	2024-07-31 22:04:12.434428	29
66	2024-08-05	2024-12-12	2024250	{"(R) Phillip Mark Seymour Burt"}	THEORIC	46	17	0	f	f	f	f	f	2024-07-31 22:04:12.434428	30
67	2024-08-05	2024-12-12	2024250	{"(R) Maria das Dores dos Santos Miranda"}	THEORIC	46	23	2	f	f	f	f	f	2024-07-31 22:04:12.434428	31
68	2024-08-05	2024-12-12	2024250	{"(R) Guido Stolfi","(R) Paul Jean Etienne Jeszensky"}	THEORIC	46	26	2	f	f	f	f	f	2024-07-31 22:04:12.434428	32
69	2024-08-05	2024-12-12	2024250	{"Cristiano Magalhaes Panazio"}	THEORIC	35	9	0	f	f	f	f	f	2024-07-31 22:04:12.434428	33
70	2024-08-05	2024-12-12	2024201	{"Juan Luis Poletti Soto"}	PRACTIC	33	7	4	f	f	f	f	f	2024-07-31 22:04:12.434428	34
71	2024-08-05	2024-12-12	2024202	{"Phillip Mark Seymour Burt"}	PRACTIC	1	1	1	f	f	f	f	f	2024-07-31 22:04:12.434428	34
72	2024-08-05	2024-12-12	2024203	{"Cristiano Magalhaes Panazio"}	PRACTIC	1	1	1	f	f	f	f	f	2024-07-31 22:04:12.434428	34
73	2024-08-05	2024-12-12	2024250	{"(R) Phillip Mark Seymour Burt"}	PRACTIC	10	8	0	f	f	f	f	f	2024-07-31 22:04:12.434428	35
74	2024-08-05	2024-12-12	2024201	{""}	THEORIC	8	6	0	f	f	f	f	f	2024-07-31 22:04:12.434428	36
75	2024-05-06	2024-08-16	2024250	{"(R) Fuad Kassab Junior"}	THEORIC	81	81	0	f	f	f	f	f	2024-07-31 22:04:12.434428	37
76	2024-08-05	2024-12-12	2024250	{""}	THEORIC	32	32	0	f	f	f	f	f	2024-07-31 22:04:12.434428	38
77	2024-08-05	2024-12-12	2024201	{"(R) Ricardo Paulino Marques"}	PRACTIC	30	30	3	f	f	f	f	f	2024-07-31 22:04:12.434428	39
78	2024-08-05	2024-12-12	2024202	{"Fuad Kassab Junior"}	PRACTIC	30	30	2	f	f	f	f	f	2024-07-31 22:04:12.434428	39
79	2024-08-05	2024-12-12	2024203	{"Felipe Miguel Pait"}	PRACTIC	30	30	2	f	f	f	f	f	2024-07-31 22:04:12.434428	39
80	2024-08-05	2024-12-12	2024204	{"Fabio de Oliveira Fialho"}	PRACTIC	31	31	4	f	f	f	f	f	2024-07-31 22:04:12.434428	39
81	2024-08-05	2024-12-12	2024205	{"Diego Colón"}	PRACTIC	30	30	2	f	f	f	f	f	2024-07-31 22:04:12.434428	39
82	2024-08-05	2024-12-12	2024201	{"Fuad Kassab Junior"}	THEORIC	102	95	4	f	f	f	f	f	2024-07-31 22:04:12.434428	40
83	2024-08-05	2024-12-12	2024202	{"Átila Madureira Bueno"}	THEORIC	102	94	3	f	f	f	f	f	2024-07-31 22:04:12.434428	40
84	2024-08-05	2024-12-12	2024203	{"Diego Colón"}	THEORIC	108	74	2	f	f	f	f	f	2024-07-31 22:04:12.434428	40
85	2024-08-05	2024-12-12	2024250	{"(R) Claudio Garcia"}	THEORIC	59	37	0	f	f	f	f	f	2024-07-31 22:04:12.434428	41
86	2024-08-05	2024-12-12	2024250	{"Felipe Miguel Pait"}	THEORIC	64	52	1	f	f	f	f	f	2024-07-31 22:04:12.434428	42
87	2024-08-05	2024-12-12	2024250	{"(R) Oswaldo Luiz do Valle Costa"}	THEORIC	59	45	0	f	f	f	f	f	2024-07-31 22:04:12.434428	43
88	2024-08-05	2024-12-12	2024250	{"(R) Ricardo Paulino Marques"}	THEORIC	59	45	1	f	f	f	f	f	2024-07-31 22:04:12.434428	44
89	2024-08-05	2024-12-12	2024250	{"(R) José Jaime da Cruz"}	THEORIC	55	14	1	f	f	f	f	f	2024-07-31 22:04:12.434428	45
90	2024-08-05	2024-12-12	2024201	{"(R) Bruno Augusto Angelico"}	THEORIC	22	22	0	f	f	f	f	f	2024-07-31 22:04:12.434428	46
91	2024-08-05	2024-12-12	2024202	{"(R) Bruno Augusto Angelico"}	THEORIC	22	16	0	f	f	f	f	f	2024-07-31 22:04:12.434428	46
92	2024-08-05	2024-12-12	2024250	{"Diego Colón"}	THEORIC	45	19	0	f	f	f	f	f	2024-07-31 22:04:12.434428	47
93	2024-08-05	2024-12-12	2024201	{"(R) Fuad Kassab Junior"}	THEORIC	5	4	2	f	f	f	f	f	2024-07-31 22:04:12.434428	48
94	2024-08-05	2024-12-12	2024202	{"Claudio Garcia"}	THEORIC	5	0	0	f	f	f	f	f	2024-07-31 22:04:12.434428	48
95	2024-08-05	2024-12-12	2024203	{"Felipe Miguel Pait"}	THEORIC	5	3	3	f	f	f	f	f	2024-07-31 22:04:12.434428	48
96	2024-08-05	2024-12-12	2024201	{"(R) Fuad Kassab Junior"}	THEORIC	15	15	0	f	f	f	f	f	2024-07-31 22:04:12.434428	49
97	2024-08-05	2024-12-12	2024202	{"Claudio Garcia"}	THEORIC	15	15	0	f	f	f	f	f	2024-07-31 22:04:12.434428	49
98	2024-08-05	2024-12-12	2024203	{"Felipe Miguel Pait"}	THEORIC	15	14	0	f	f	f	f	f	2024-07-31 22:04:12.434428	49
99	2024-08-05	2024-12-12	2024250	{"(R) Felipe Miguel Pait","(R) Fuad Kassab Junior","(R) Pedro Luiz Pizzigatti Corrêa"}	THEORIC	55	30	0	f	f	f	f	f	2024-07-31 22:04:12.434428	50
100	2024-08-05	2024-12-12	2024250	{"(R) Luiz Henrique Alves Monteiro"}	THEORIC	55	16	1	f	f	f	f	f	2024-07-31 22:04:12.434428	51
101	2024-08-05	2024-12-12	2024250	{"(R) Henrique Takachi Moriya"}	THEORIC	36	10	1	f	f	f	f	f	2024-07-31 22:04:12.434428	52
102	2024-08-05	2024-12-12	2024201	{"(R) Sebastião Gomes dos Santos Filho","Armando Antonio Maria Lagana"}	THEORIC	94	98	4	f	f	f	f	f	2024-07-31 22:04:12.434428	53
103	2024-08-05	2024-12-12	2024201	{"João Francisco Justo Filho"}	THEORIC	84	98	8	f	f	f	f	f	2024-07-31 22:04:12.434428	54
104	2024-08-05	2024-12-12	2024201	{"Miguel Arjona Ramirez"}	THEORIC	82	74	2	f	f	f	f	f	2024-07-31 22:04:12.434428	55
105	2024-08-05	2024-12-12	2024202	{"(R) Magno Teófilo Madeira da Silva","Elisabete Galeazzo"}	THEORIC	82	79	4	f	f	f	f	f	2024-07-31 22:04:12.434428	55
106	2024-08-05	2024-12-12	2024203	{"(R) Flávio Almeida de Magalhães Cipparrone"}	THEORIC	77	75	3	f	f	f	f	f	2024-07-31 22:04:12.434428	55
107	2024-08-05	2024-12-12	2024204	{"Wagner Luiz Zucchi"}	THEORIC	83	42	4	f	f	f	f	f	2024-07-31 22:04:12.434428	55
108	2024-08-05	2024-12-12	2024201	{"(R) Antonio Carlos Seabra","(R) Magno Teófilo Madeira da Silva"}	THEORIC	50	11	1	f	f	f	f	f	2024-07-31 22:04:12.434428	56
109	2024-08-05	2024-12-12	2024201	{"(R) Sebastião Gomes dos Santos Filho"}	THEORIC	66	47	3	f	f	f	f	f	2024-07-31 22:04:12.434428	57
110	2024-08-05	2024-12-12	2024201	{"(R) Antonio Carlos Seabra"}	THEORIC	80	79	4	f	f	f	f	f	2024-07-31 22:04:12.434428	58
111	2024-08-05	2024-12-12	2024202	{"(R) João Antonio Martino"}	THEORIC	80	63	4	f	f	f	f	f	2024-07-31 22:04:12.434428	58
112	2024-08-05	2024-12-12	2024201	{"(R) Gustavo Pamplona Rehder","(R) Hae Yong Kim"}	PRACTIC	52	43	0	f	f	f	f	f	2024-07-31 22:04:12.434428	59
113	2024-08-05	2024-12-12	2024201	{"(R) Vitor Heloiz Nascimento"}	THEORIC	44	36	0	f	f	f	f	f	2024-07-31 22:04:12.434428	60
114	2024-08-05	2024-12-12	2024201	{"Marcelo Knorich Zuffo"}	THEORIC	59	37	2	f	f	f	f	f	2024-07-31 22:04:12.434428	62
115	2024-08-05	2024-12-12	2024201	{"(R) Ariana Maria da Conceição Lacorte Caniato Serrano","Bruno Cavalcante de Souza Sanches"}	VINCULATED_THEORIC	35	23	0	f	f	f	f	f	2024-07-31 22:04:12.434428	63
116	2024-08-05	2024-12-12	2024212	{"(R) Ariana Maria da Conceição Lacorte Caniato Serrano","Bruno Cavalcante de Souza Sanches"}	VINCULATED_PRACTIC	25	23	0	f	f	f	f	f	2024-07-31 22:04:12.434428	63
117	2024-08-05	2024-12-12	2024201	{"(R) Fernando Josepetti Fonseca"}	THEORIC	30	7	0	f	f	f	f	f	2024-07-31 22:04:12.434428	64
118	2024-08-05	2024-12-12	2024201	{"(R) Fernando Josepetti Fonseca","(R) Leopoldo Rideki Yoshioka"}	THEORIC	62	21	0	f	f	f	f	f	2024-07-31 22:04:12.434428	65
119	2024-08-05	2024-12-12	2024201	{"(R) Hae Yong Kim","(R) Marcio Lobo Netto"}	THEORIC	80	37	0	f	f	f	f	f	2024-07-31 22:04:12.434428	66
120	2024-08-05	2024-12-12	2024201	{"(R) Ariana Maria da Conceição Lacorte Caniato Serrano","(R) Wagner Luiz Zucchi"}	THEORIC	55	27	0	f	f	f	f	f	2024-07-31 22:04:12.434428	67
121	2024-08-05	2024-12-12	2024201	{"(R) Fatima Salete Correra"}	THEORIC	47	22	0	f	f	f	f	f	2024-07-31 22:04:12.434428	68
122	2024-08-05	2024-12-12	2024201	{"(R) Miguel Arjona Ramirez"}	THEORIC	36	5	0	f	f	f	f	f	2024-07-31 22:04:12.434428	69
123	2024-08-05	2024-12-12	2024201	{"(R) Marcelo Knorich Zuffo","(R) Roseli de Deus Lopes"}	THEORIC	118	42	6	f	f	f	f	f	2024-07-31 22:04:12.434428	70
124	2024-08-05	2024-12-12	2024201	{"(R) Sergio Takeo Kofuji"}	THEORIC	65	25	1	f	f	f	f	f	2024-07-31 22:04:12.434428	71
125	2024-08-05	2024-12-12	2024201	{"(R) Marcio Lobo Netto"}	THEORIC	66	42	2	f	f	f	f	f	2024-07-31 22:04:12.434428	72
126	2024-08-05	2024-12-12	2024201	{"(R) Antonio Carlos Seabra","(R) Marcelo Knorich Zuffo","Roseli de Deus Lopes"}	THEORIC	56	39	1	f	f	f	f	f	2024-07-31 22:04:12.434428	73
127	2024-08-05	2024-12-12	2024201	{"(R) Fernando Josepetti Fonseca","(R) Sergio Takeo Kofuji","Ariana Maria da Conceição Lacorte Caniato Serrano"}	THEORIC	50	21	0	f	f	f	f	f	2024-07-31 22:04:12.434428	74
128	2024-08-05	2024-12-12	2024201	{""}	PRACTIC	25	27	1	f	f	f	f	f	2024-07-31 22:04:12.434428	75
129	2024-08-05	2024-12-12	2024202	{""}	PRACTIC	25	26	1	f	f	f	f	f	2024-07-31 22:04:12.434428	75
130	2024-08-05	2024-12-12	2024203	{""}	PRACTIC	25	25	2	f	f	f	f	f	2024-07-31 22:04:12.434428	75
131	2024-08-05	2024-12-12	2024204	{""}	PRACTIC	25	22	0	f	f	f	f	f	2024-07-31 22:04:12.434428	75
132	2024-08-05	2024-12-12	2024205	{""}	PRACTIC	25	25	0	f	f	f	f	f	2024-07-31 22:04:12.434428	75
133	2024-08-05	2024-12-12	2024206	{""}	PRACTIC	25	24	0	f	f	f	f	f	2024-07-31 22:04:12.434428	75
134	2024-08-05	2024-12-12	2024201	{"(R) João Antonio Martino","(R) Marcelo Nelson Paez Carreno"}	THEORIC	15	10	0	f	f	f	f	f	2024-07-31 22:04:12.434428	76
135	2024-08-05	2024-12-12	2024201	{"(R) Ricardo Nakamura"}	PRACTIC	24	25	0	f	f	f	f	f	2024-07-31 22:04:12.434428	77
136	2024-08-05	2024-12-12	2024202	{"(R) Romero Tori"}	PRACTIC	21	20	0	f	f	f	f	f	2024-07-31 22:04:12.434428	77
137	2024-08-05	2024-12-12	2024201	{"(R) Anna Helena Reali Costa"}	THEORIC	75	71	15	f	f	f	f	f	2024-07-31 22:04:12.434428	78
138	2024-08-05	2024-12-12	2024202	{"(R) Artur Jordão Lima Correia"}	THEORIC	75	66	18	f	f	f	f	f	2024-07-31 22:04:12.434428	78
139	2024-08-05	2024-12-12	2024203	{"(R) Anarosa Alves Franco Brandão"}	THEORIC	75	72	18	f	f	f	f	f	2024-07-31 22:04:12.434428	78
140	2024-08-05	2024-12-12	2024201	{"(R) Pedro Luiz Pizzigatti Corrêa"}	PRACTIC	27	22	2	f	f	f	f	f	2024-07-31 22:04:12.434428	79
141	2024-08-05	2024-12-12	2024202	{"Ricardo Nakamura"}	PRACTIC	28	21	4	f	f	f	f	f	2024-07-31 22:04:12.434428	79
142	2024-08-05	2024-12-12	2024203	{"Artur Jordão Lima Correia"}	PRACTIC	27	28	0	f	f	f	f	f	2024-07-31 22:04:12.434428	79
143	2024-08-05	2024-12-12	2024204	{"(R) Solange Nice Alves de Souza"}	PRACTIC	27	27	0	f	f	f	f	f	2024-07-31 22:04:12.434428	79
144	2024-08-05	2024-12-12	2024205	{"(R) Fabio Levy Siqueira"}	PRACTIC	27	24	0	f	f	f	f	f	2024-07-31 22:04:12.434428	79
145	2024-08-05	2024-12-12	2024206	{"(R) Kechi Hirama"}	PRACTIC	27	24	2	f	f	f	f	f	2024-07-31 22:04:12.434428	79
146	2024-08-05	2024-12-12	2024207	{"Anarosa Alves Franco Brandão"}	PRACTIC	27	31	0	f	f	f	f	f	2024-07-31 22:04:12.434428	79
147	2024-08-05	2024-12-12	2024204	{"(R) Edson Satoshi Gomi"}	THEORIC	48	59	0	f	f	f	f	f	2024-07-31 22:04:12.434428	80
148	2024-08-05	2024-12-12	2024205	{"(R) Bruno de Carvalho Albertini"}	THEORIC	49	51	1	f	f	f	f	f	2024-07-31 22:04:12.434428	80
149	2024-08-05	2024-12-12	2024251	{"(R) Selma Shin Shimizu Melnikoff"}	THEORIC	43	38	0	f	f	f	f	f	2024-07-31 22:04:12.434428	81
150	2024-08-05	2024-12-12	2024252	{"(R) Jorge Luis Risco Becerra"}	THEORIC	42	42	2	f	f	f	f	f	2024-07-31 22:04:12.434428	81
151	2024-08-05	2024-12-12	2024201	{"","(R) Marco Tulio Carvalho de Andrade"}	THEORIC	75	77	7	f	f	f	f	f	2024-07-31 22:04:12.434428	82
152	2024-08-05	2024-12-12	2024202	{"","Bruno Abrantes Basseto"}	THEORIC	75	77	4	f	f	f	f	f	2024-07-31 22:04:12.434428	82
153	2024-08-05	2024-12-12	2024203	{"(R) Glauber De Bona"}	THEORIC	75	63	4	f	f	f	f	f	2024-07-31 22:04:12.434428	82
154	2024-08-05	2024-12-12	2024250	{"(R) Ricardo Nakamura"}	THEORIC	29	52	0	f	f	f	f	f	2024-07-31 22:04:12.434428	83
155	2024-08-05	2024-12-12	2024201	{"(R) Carlos Eduardo Cugnasca"}	PRACTIC	6	6	0	f	f	f	f	f	2024-07-31 22:04:12.434428	84
156	2024-08-05	2024-12-12	2024202	{"Moacyr Martucci Junior"}	PRACTIC	3	4	0	f	f	f	f	f	2024-07-31 22:04:12.434428	84
157	2024-08-05	2024-12-12	2024203	{"(R) Carlos Eduardo Cugnasca"}	PRACTIC	3	2	1	f	f	f	f	f	2024-07-31 22:04:12.434428	84
158	2024-08-05	2024-12-12	2024250	{""}	THEORIC	4	3	0	f	f	f	f	f	2024-07-31 22:04:12.434428	85
159	2024-08-05	2024-12-12	2024201	{"(R) João Batista Camargo Júnior","(R) Paulo Sergio Cugnasca"}	PRACTIC	25	24	3	f	f	f	f	f	2024-07-31 22:04:12.434428	86
160	2024-08-05	2024-12-12	2024252	{"(R) Jorge Luis Risco Becerra"}	PRACTIC	10	2	0	f	f	f	f	f	2024-07-31 22:04:12.434428	87
161	2024-08-05	2024-12-12	2024250	{"(R) Liria Matsumoto Sato"}	THEORIC	13	8	0	f	f	f	f	f	2024-07-31 22:04:12.434428	89
162	2024-08-05	2024-12-12	2024250	{"(R) Pedro Luiz Pizzigatti Corrêa"}	THEORIC	13	8	0	f	f	f	f	f	2024-07-31 22:04:12.434428	90
163	2024-08-05	2024-12-12	2024250	{"(R) João Batista Camargo Júnior"}	THEORIC	11	8	0	f	f	f	f	f	2024-07-31 22:04:12.434428	91
164	2024-08-05	2024-12-12	2024201	{"(R) Edson Satoshi Gomi"}	THEORIC	12	10	0	f	f	f	f	f	2024-07-31 22:04:12.434428	92
165	2024-05-06	2024-08-16	2024251	{"(R) Cíntia Borges Margi"}	THEORIC	42	36	0	f	f	f	f	f	2024-07-31 22:04:12.434428	93
166	2024-05-06	2024-08-16	2024252	{"(R) Wilson Vicente Ruggiero"}	THEORIC	40	36	0	f	f	f	f	f	2024-07-31 22:04:12.434428	93
167	2024-05-06	2024-08-16	2024251	{"(R) Tereza Cristina Melo de Brito Carvalho"}	THEORIC	37	34	0	f	f	f	f	f	2024-07-31 22:04:12.434428	94
168	2024-05-06	2024-08-16	2024252	{"(R) Regina Melo Silveira"}	THEORIC	37	33	0	f	f	f	f	f	2024-07-31 22:04:12.434428	94
169	2024-08-05	2024-12-12	2024250	{"Regina Melo Silveira"}	THEORIC	15	15	0	f	f	f	f	f	2024-07-31 22:04:12.434428	95
172	2024-08-05	2024-12-12	2024250	{"Cristina Gomes Fernandes"}	THEORIC	86	88	7	f	f	f	f	f	2024-07-31 22:04:12.434428	96
174	2024-08-05	2024-12-12	2024201	{"(R) Alberto Hernandez Neto"}	THEORIC	60	60	1	f	f	f	f	f	2024-07-31 22:04:12.434428	97
175	2024-08-05	2024-12-12	2024202	{"Maurício Silva Ferreira"}	THEORIC	60	60	2	f	f	f	f	f	2024-07-31 22:04:12.434428	97
176	2024-08-05	2024-12-12	2024203	{"Jurandir Itizo Yanagihara"}	THEORIC	60	62	2	f	f	f	f	f	2024-07-31 22:04:12.434428	97
177	2024-08-05	2024-12-12	2024204	{"Flávio Augusto Sanzovo Fiorelli"}	THEORIC	60	55	4	f	f	f	f	f	2024-07-31 22:04:12.434428	97
178	2024-08-05	2024-12-12	2024201	{"Jose Joaquim do Amaral Ferreira"}	THEORIC	100	98	2	f	f	f	f	f	2024-07-31 22:04:12.434428	98
179	2024-08-05	2024-12-12	2024202	{"Daniel de Oliveira Mota"}	THEORIC	80	90	3	f	f	f	f	f	2024-07-31 22:04:12.434428	98
180	2024-08-05	2024-12-12	2024203	{"Alberto Wunderler Ramos"}	THEORIC	81	63	0	f	f	f	f	f	2024-07-31 22:04:12.434428	98
181	2024-08-05	2024-12-12	2024204	{"Alberto Wunderler Ramos"}	THEORIC	100	96	5	f	f	f	f	f	2024-07-31 22:04:12.434428	98
182	2024-08-05	2024-12-12	2024205	{"Regina Meyer Branski"}	THEORIC	80	85	1	f	f	f	f	f	2024-07-31 22:04:12.434428	98
183	2024-08-05	2024-12-12	2024206	{"Jose Joaquim do Amaral Ferreira"}	THEORIC	80	67	8	f	f	f	f	f	2024-07-31 22:04:12.434428	98
184	2024-08-05	2024-12-12	2024208	{"Miguel Angelo de Carvalho Michalski"}	THEORIC	81	64	4	f	f	f	f	f	2024-07-31 22:04:12.434428	98
185	2024-08-05	2024-12-12	2024209	{"Miguel Angelo de Carvalho Michalski"}	THEORIC	100	100	8	f	f	f	f	f	2024-07-31 22:04:12.434428	98
186	2024-08-05	2024-12-12	2024210	{"Renan Favarão da Silva"}	THEORIC	100	98	2	f	f	f	f	f	2024-07-31 22:04:12.434428	98
187	2024-08-05	2024-12-12	2024201	{"João Amato Neto"}	THEORIC	50	56	0	f	f	f	f	f	2024-07-31 22:04:12.434428	99
188	2024-08-05	2024-12-12	2024202	{"Paulino Graciano Francischini"}	THEORIC	101	103	11	f	f	f	f	f	2024-07-31 22:04:12.434428	99
189	2024-08-05	2024-12-12	2024201	{"João Amato Neto"}	THEORIC	92	93	0	f	f	f	f	f	2024-07-31 22:04:12.434428	100
190	2024-08-05	2024-12-12	2024202	{"Roberta de Castro Souza Piao"}	THEORIC	93	98	0	f	f	f	f	f	2024-07-31 22:04:12.434428	100
191	2024-08-05	2024-12-12	2024203	{"(R) Reinaldo Pacheco da Costa"}	THEORIC	92	92	0	f	f	f	f	f	2024-07-31 22:04:12.434428	100
192	2024-08-05	2024-12-12	2024204	{"Roberta de Castro Souza Piao"}	THEORIC	80	88	2	f	f	f	f	f	2024-07-31 22:04:12.434428	100
193	2024-08-05	2024-12-12	2024201	{"Renato Higa"}	THEORIC	94	97	15	f	f	f	f	f	2024-07-31 22:04:12.434428	101
194	2024-08-05	2024-12-12	2024202	{"Luis Gregorio Godoy de Vasconcellos Dias da Silva"}	THEORIC	85	86	8	f	f	f	f	f	2024-07-31 22:04:12.434428	101
195	2024-08-05	2024-12-12	2024203	{"Luis Gregorio Godoy de Vasconcellos Dias da Silva"}	THEORIC	86	82	14	f	f	f	f	f	2024-07-31 22:04:12.434428	101
196	2024-08-05	2024-12-12	2024204	{"Luis Gregorio Godoy de Vasconcellos Dias da Silva"}	THEORIC	85	70	4	f	f	f	f	f	2024-07-31 22:04:12.434428	101
197	2024-08-05	2024-12-12	2024205	{"Luis Gregorio Godoy de Vasconcellos Dias da Silva"}	THEORIC	85	53	2	f	f	f	f	f	2024-07-31 22:04:12.434428	101
198	2024-08-05	2024-12-12	2024206	{"Euzi Conceicao Fernandes da Silva"}	THEORIC	85	58	5	f	f	f	f	f	2024-07-31 22:04:12.434428	101
199	2024-08-05	2024-12-12	2024207	{"Luis Gregorio Godoy de Vasconcellos Dias da Silva"}	THEORIC	85	86	8	f	f	f	f	f	2024-07-31 22:04:12.434428	101
200	2024-08-05	2024-12-12	2024208	{"Luis Gregorio Godoy de Vasconcellos Dias da Silva"}	THEORIC	100	102	21	f	f	f	f	f	2024-07-31 22:04:12.434428	101
201	2024-08-05	2024-12-12	2024209	{"Renato Higa"}	THEORIC	85	86	12	f	f	f	f	f	2024-07-31 22:04:12.434428	101
202	2024-08-05	2024-12-12	2024210	{"Renato Higa"}	THEORIC	85	75	6	f	f	f	f	f	2024-07-31 22:04:12.434428	101
203	2024-08-05	2024-12-12	2024211	{"Euzi Conceicao Fernandes da Silva"}	THEORIC	85	43	0	f	f	f	f	f	2024-07-31 22:04:12.434428	101
204	2024-08-05	2024-12-12	2024212	{"Renato Higa"}	THEORIC	85	75	10	f	f	f	f	f	2024-07-31 22:04:12.434428	101
205	2024-08-05	2024-12-12	2024201	{"(R) Giovanni Manassero Junior"}	THEORIC	61	28	19	f	f	f	f	f	2024-07-31 22:04:12.434428	102
206	2024-08-05	2024-12-12	2024201	{"Deborah Martins Raphael"}	THEORIC	85	106	7	f	f	f	f	f	2024-08-02 19:15:49.620891	103
207	2024-08-05	2024-12-12	2024202	{"Leonardo Pellegrini Rodrigues"}	THEORIC	86	126	3	f	f	f	f	f	2024-08-02 19:15:49.620891	103
208	2024-08-05	2024-12-12	2024203	{"Leonardo Pellegrini Rodrigues"}	THEORIC	85	120	5	f	f	f	f	f	2024-08-02 19:15:49.620891	103
209	2024-08-05	2024-12-12	2024204	{"Glaucio Terra"}	THEORIC	85	99	4	f	f	f	f	f	2024-08-02 19:15:49.620891	103
210	2024-08-05	2024-12-12	2024205	{"Glaucio Terra"}	THEORIC	85	108	7	f	f	f	f	f	2024-08-02 19:15:49.620891	103
211	2024-08-05	2024-12-12	2024206	{"Deborah Martins Raphael"}	THEORIC	85	103	5	f	f	f	f	f	2024-08-02 19:15:49.620891	103
212	2024-08-05	2024-12-12	2024207	{"Wilson Albeiro Cuellar Carrera"}	THEORIC	85	109	6	f	f	f	f	f	2024-08-02 19:15:49.620891	103
213	2024-08-05	2024-12-12	2024208	{"João Fernando da Cunha Nariyoshi"}	THEORIC	85	111	12	f	f	f	f	f	2024-08-02 19:15:49.620891	103
214	2024-08-05	2024-12-12	2024209	{"João Fernando da Cunha Nariyoshi"}	THEORIC	85	99	12	f	f	f	f	f	2024-08-02 19:15:49.620891	103
215	2024-08-05	2024-12-12	2024210	{"Henrique Guzzo Junior"}	THEORIC	85	109	6	f	f	f	f	f	2024-08-02 19:15:49.620891	103
216	2024-08-05	2024-12-12	2024211	{"Alexandre Lymberopoulos"}	THEORIC	85	45	0	f	f	f	f	f	2024-08-02 19:15:49.620891	103
217	2024-08-05	2024-12-12	2024212	{"Wilson Albeiro Cuellar Carrera"}	THEORIC	85	97	8	f	f	f	f	f	2024-08-02 19:15:49.620891	103
228	2024-08-05	2024-12-12	2024201	{"Andre Bohomoletz Henriques"}	THEORIC	85	97	1	f	f	f	f	f	2024-08-02 19:15:49.620891	104
229	2024-08-05	2024-12-12	2024202	{"Andre Bohomoletz Henriques"}	THEORIC	85	81	10	f	f	f	f	f	2024-08-02 19:15:49.620891	104
230	2024-08-05	2024-12-12	2024203	{"Marco Aurélio Brizzotti Andrade"}	THEORIC	80	84	2	f	f	f	f	f	2024-08-02 19:15:49.620891	104
231	2024-08-05	2024-12-12	2024204	{"Marco Aurélio Brizzotti Andrade"}	THEORIC	80	45	0	f	f	f	f	f	2024-08-02 19:15:49.620891	104
232	2024-08-05	2024-12-12	2024205	{"Ricardo de Lima"}	THEORIC	80	67	12	f	f	f	f	f	2024-08-02 19:15:49.620891	104
233	2024-08-05	2024-12-12	2024206	{"Ricardo de Lima"}	THEORIC	80	39	3	f	f	f	f	f	2024-08-02 19:15:49.620891	104
234	2024-08-05	2024-12-12	2024207	{"Fernando Tadeu Caldeira Brandt"}	THEORIC	80	74	5	f	f	f	f	f	2024-08-02 19:15:49.620891	104
235	2024-08-05	2024-12-12	2024208	{"Fernando Tadeu Caldeira Brandt"}	THEORIC	70	51	2	f	f	f	f	f	2024-08-02 19:15:49.620891	104
236	2024-08-05	2024-12-12	2024209	{"Carla Goldman"}	THEORIC	80	71	2	f	f	f	f	f	2024-08-02 19:15:49.620891	104
237	2024-08-05	2024-12-12	2024250	{""}	THEORIC	150	174	1	f	f	f	f	f	2024-08-02 19:15:49.620891	105
241	2024-08-05	2024-12-12	2024201	{"Jaime Angulo Pava"}	THEORIC	85	95	0	f	f	f	f	f	2024-08-02 19:15:49.620891	107
242	2024-08-05	2024-12-12	2024202	{"Jaime Angulo Pava"}	THEORIC	85	91	2	f	f	f	f	f	2024-08-02 19:15:49.620891	107
243	2024-08-05	2024-12-12	2024203	{"Claudio Gorodski"}	THEORIC	85	93	1	f	f	f	f	f	2024-08-02 19:15:49.620891	107
244	2024-08-05	2024-12-12	2024204	{"Claudio Gorodski"}	THEORIC	85	85	1	f	f	f	f	f	2024-08-02 19:15:49.620891	107
245	2024-08-05	2024-12-12	2024205	{"Edson de Faria"}	THEORIC	87	84	5	f	f	f	f	f	2024-08-02 19:15:49.620891	107
246	2024-08-05	2024-12-12	2024206	{"Edson de Faria"}	THEORIC	85	90	2	f	f	f	f	f	2024-08-02 19:15:49.620891	107
247	2024-08-05	2024-12-12	2024207	{"Martha Patrícia Dussan Angulo"}	THEORIC	85	86	2	f	f	f	f	f	2024-08-02 19:15:49.620891	107
248	2024-08-05	2024-12-12	2024208	{"Martha Patrícia Dussan Angulo"}	THEORIC	85	46	0	f	f	f	f	f	2024-08-02 19:15:49.620891	107
249	2024-08-05	2024-12-12	2024209	{"Ricardo dos Santos Freire Junior"}	THEORIC	85	63	1	f	f	f	f	f	2024-08-02 19:15:49.620891	107
250	2024-08-05	2024-12-12	2024210	{"Ricardo dos Santos Freire Junior"}	THEORIC	85	76	1	f	f	f	f	f	2024-08-02 19:15:49.620891	107
255	2024-08-05	2024-12-12	2024201	{"Ronaldo de Breyne Salvagni"}	THEORIC	75	75	12	f	f	f	f	f	2024-08-02 19:15:49.620891	109
256	2024-08-05	2024-12-12	2024202	{"Demetrio Cornilios Zachariadis"}	THEORIC	75	70	10	f	f	f	f	f	2024-08-02 19:15:49.620891	109
257	2024-08-05	2024-12-12	2024203	{"Flavio Celso Trigo"}	THEORIC	75	74	11	f	f	f	f	f	2024-08-02 19:15:49.620891	109
258	2024-08-05	2024-12-12	2024204	{"Guilherme Jorge Vernizzi Lopes"}	THEORIC	75	79	3	f	f	f	f	f	2024-08-02 19:15:49.620891	109
259	2024-08-05	2024-12-12	2024205	{"Flavius Portella Ribas Martins"}	THEORIC	75	69	3	f	f	f	f	f	2024-08-02 19:15:49.620891	109
260	2024-08-05	2024-12-12	2024206	{"(R) Renato Maia Matarazzo Orsino"}	THEORIC	75	70	5	f	f	f	f	f	2024-08-02 19:15:49.620891	109
261	2024-08-05	2024-12-12	2024207	{"Éverton Lins de Oliveira"}	THEORIC	75	75	5	f	f	f	f	f	2024-08-02 19:15:49.620891	109
262	2024-08-05	2024-12-12	2024208	{"Ronaldo Carrion"}	THEORIC	78	73	18	f	f	f	f	f	2024-08-02 19:15:49.620891	109
263	2024-08-05	2024-12-12	2024209	{"Edilson Hiroshi Tamai"}	THEORIC	76	75	9	f	f	f	f	f	2024-08-02 19:15:49.620891	109
264	2024-08-05	2024-12-12	2024210	{"Roberto Martins de Souza"}	THEORIC	75	57	5	f	f	f	f	f	2024-08-02 19:15:49.620891	109
265	2024-08-05	2024-12-12	2024211	{"(R) Francisco José Profito"}	THEORIC	75	69	7	f	f	f	f	f	2024-08-02 19:15:49.620891	109
266	2024-08-05	2024-12-12	2024212	{"Roberto Spinola Barbosa"}	THEORIC	75	69	7	f	f	f	f	f	2024-08-02 19:15:49.620891	109
267	2024-08-05	2024-12-12	2024201	{"(R) Clovis de Arruda Martins"}	THEORIC	60	56	3	f	f	f	f	f	2024-08-02 19:15:49.620891	110
268	2024-08-05	2024-12-12	2024202	{"(R) Roberto Ramos Junior"}	THEORIC	60	56	7	f	f	f	f	f	2024-08-02 19:15:49.620891	110
269	2024-08-05	2024-12-12	2024201	{"Elizabeth Grillo Fernandes"}	THEORIC	77	60	1	f	f	f	f	f	2024-08-02 19:15:49.620891	111
270	2024-08-05	2024-12-12	2024202	{"Eduardo Franco de Monlevade"}	THEORIC	83	88	10	f	f	f	f	f	2024-08-02 19:15:49.620891	111
271	2024-08-05	2024-12-12	2024203	{"Antonio Carlos Vieira Coelho"}	THEORIC	79	52	1	f	f	f	f	f	2024-08-02 19:15:49.620891	111
272	2024-08-05	2024-12-12	2024204	{"Antonio Carlos Vieira Coelho"}	THEORIC	77	72	3	f	f	f	f	f	2024-08-02 19:15:49.620891	111
273	2024-08-05	2024-12-12	2024205	{"Andre Luiz da Silva"}	THEORIC	78	51	0	f	f	f	f	f	2024-08-02 19:15:49.620891	111
274	2024-08-05	2024-12-12	2024201	{"Wang Shu Hui"}	THEORIC	79	49	1	f	f	f	f	f	2024-08-02 19:15:49.620891	112
275	2024-08-05	2024-12-12	2024202	{"Patrícia Schmid Calvão"}	THEORIC	81	39	0	f	f	f	f	f	2024-08-02 19:15:49.620891	112
276	2024-08-05	2024-12-12	2024203	{"Elizabeth Grillo Fernandes"}	THEORIC	78	53	1	f	f	f	f	f	2024-08-02 19:15:49.620891	112
277	2024-08-05	2024-12-12	2024205	{"Andre Luiz da Silva"}	THEORIC	81	42	15	f	f	f	f	f	2024-08-02 19:15:49.620891	112
278	2024-08-05	2024-12-12	2024206	{"Fernando Jose Gomes Landgraf"}	THEORIC	89	70	4	f	f	f	f	f	2024-08-02 19:15:49.620891	112
279	2024-08-05	2024-12-12	2024250	{"","Eduardo Franco de Monlevade","Ticiane Sanches Valera"}	THEORIC	107	76	6	f	f	f	f	f	2024-08-02 19:15:49.620891	113
280	2024-08-05	2024-12-11	2024201	{"(R) Antonio Carlos Silva Costa Teixeira"}	VINCULATED_THEORIC	71	71	3	f	f	f	f	f	2024-08-02 19:15:49.620891	114
281	2024-08-05	2024-12-11	2024202	{"Denise Crocce Romano Espinosa","Jorge Alberto Soares Tenório"}	VINCULATED_THEORIC	69	69	0	f	f	f	f	f	2024-08-02 19:15:49.620891	114
282	2024-08-05	2024-12-11	2024203	{"Denise Crocce Romano Espinosa","Jorge Alberto Soares Tenório"}	VINCULATED_THEORIC	63	63	0	f	f	f	f	f	2024-08-02 19:15:49.620891	114
238	2024-08-05	2024-12-12	2024201	{"Não informado"}	THEORIC	0	0	0	f	f	f	f	f	2024-08-02 19:15:49.620891	106
251	2024-08-05	2024-12-12	2024201	{"(R) Rodrigo Provasi Correia"}	THEORIC	58	43	0	f	f	f	f	f	2024-08-02 19:15:49.620891	108
289	2024-08-05	2024-12-11	2024201	{"","(R) José Luis Pires Camacho","Ardson dos Santos Vianna Junior","José Luis de Paiva","Martina Costa Reis"}	VINCULATED_THEORIC	68	64	0	f	f	f	f	f	2024-08-02 19:15:49.620891	115
305	2024-09-02	2024-12-13	2024301	{"Daniel Ribeiro Gomes"}	THEORIC	68	0	0	f	f	f	f	f	2024-08-02 19:15:49.620891	118
308	2024-08-05	2024-12-12	2024201	{"(R) Marcelo Augusto Leal Alves","Francisco José Profito","Juliane Ribeiro da Cruz Alves"}	VINCULATED_THEORIC	90	91	1	f	f	f	f	f	2024-08-02 19:15:49.620891	124
309	2024-08-05	2024-12-12	2024231	{"Francisco José Profito","Juliane Ribeiro da Cruz Alves"}	VINCULATED_PRACTIC	29	29	0	f	f	f	f	f	2024-08-02 19:15:49.620891	124
304	2024-08-05	2024-12-12	2024201	{"(R) Antonio Carlos Seabra","(R) Marcelo Knorich Zuffo","Roseli de Deus Lopes"}	THEORIC	50	7	0	f	f	f	f	f	2024-08-02 19:15:49.620891	117
341	2024-08-05	2024-12-12	2024201	{"(R) Marcelo Augusto Leal Alves"}	THEORIC	60	24	0	f	f	f	f	f	2024-08-02 19:15:49.620891	129
306	2024-08-05	2024-12-12	2024201	{"(R) Marcelo Augusto Leal Alves"}	PRACTIC	42	45	0	f	f	f	f	f	2024-08-02 19:15:49.620891	123
307	2024-08-05	2024-12-12	2024202	{"(R) Marcelo Augusto Leal Alves"}	PRACTIC	42	43	0	f	f	f	f	f	2024-08-02 19:15:49.620891	123
291	2024-08-05	2024-12-12	2024201	{"Vitor de Oliveira Ferreira"}	THEORIC	85	105	10	f	f	f	f	f	2024-08-02 19:15:49.620891	116
292	2024-08-05	2024-12-12	2024202	{"Javier Sanchez Serdà"}	THEORIC	85	93	3	f	f	f	f	f	2024-08-02 19:15:49.620891	116
293	2024-08-05	2024-12-12	2024203	{"Javier Sanchez Serdà"}	THEORIC	85	97	5	f	f	f	f	f	2024-08-02 19:15:49.620891	116
294	2024-08-05	2024-12-12	2024204	{"Kostiantyn Iusenko"}	THEORIC	85	95	11	f	f	f	f	f	2024-08-02 19:15:49.620891	116
295	2024-08-05	2024-12-12	2024205	{"Kostiantyn Iusenko"}	THEORIC	85	92	8	f	f	f	f	f	2024-08-02 19:15:49.620891	116
296	2024-08-05	2024-12-12	2024206	{"Vitor de Oliveira Ferreira"}	THEORIC	85	94	6	f	f	f	f	f	2024-08-02 19:15:49.620891	116
297	2024-08-05	2024-12-12	2024207	{"Daniel Victor Tausk"}	THEORIC	86	88	10	f	f	f	f	f	2024-08-02 19:15:49.620891	116
298	2024-08-05	2024-12-12	2024208	{""}	THEORIC	85	92	20	f	f	f	f	f	2024-08-02 19:15:49.620891	116
299	2024-08-05	2024-12-12	2024209	{""}	THEORIC	85	90	10	f	f	f	f	f	2024-08-02 19:15:49.620891	116
300	2024-08-05	2024-12-12	2024210	{"Valentin Raphael Henri Ferenczi"}	THEORIC	85	100	8	f	f	f	f	f	2024-08-02 19:15:49.620891	116
301	2024-08-05	2024-12-12	2024211	{"Alexandre Lymberopoulos"}	THEORIC	85	45	0	f	f	f	f	f	2024-08-02 19:15:49.620891	116
302	2024-08-05	2024-12-12	2024212	{"Daniel Victor Tausk"}	THEORIC	85	94	7	f	f	f	f	f	2024-08-02 19:15:49.620891	116
313	2024-08-05	2024-12-12	2024211	{"(R) Flavius Portella Ribas Martins","Walter Jorge Augusto Ponge Ferreira"}	THEORIC	22	8	0	f	f	f	f	f	2024-08-02 19:15:49.620891	125
314	2024-08-05	2024-12-12	2024212	{"(R) Flavius Portella Ribas Martins","Walter Jorge Augusto Ponge Ferreira"}	THEORIC	25	25	0	f	f	f	f	f	2024-08-02 19:15:49.620891	125
315	2024-08-05	2024-12-12	2024221	{"(R) Flavius Portella Ribas Martins","Walter Jorge Augusto Ponge Ferreira"}	THEORIC	22	17	1	f	f	f	f	f	2024-08-02 19:15:49.620891	125
316	2024-08-05	2024-12-12	2024222	{"(R) Flavius Portella Ribas Martins","Walter Jorge Augusto Ponge Ferreira"}	THEORIC	22	13	0	f	f	f	f	f	2024-08-02 19:15:49.620891	125
323	2024-08-05	2024-12-12	2024201	{"(R) Antonio Luis de Campos Mariani"}	VINCULATED_THEORIC	88	88	10	f	f	f	f	f	2024-08-02 19:15:49.620891	128
324	2024-08-05	2024-12-12	2024202	{"Jayme Pinto Ortiz"}	VINCULATED_THEORIC	90	104	2	f	f	f	f	f	2024-08-02 19:15:49.620891	128
325	2024-08-05	2024-12-12	2024203	{"Marcos Tadeu Pereira"}	VINCULATED_THEORIC	63	43	4	f	f	f	f	f	2024-08-02 19:15:49.620891	128
326	2024-08-05	2024-12-12	2024204	{"(R) Antonio Luis de Campos Mariani"}	VINCULATED_THEORIC	72	78	9	f	f	f	f	f	2024-08-02 19:15:49.620891	128
327	2024-08-05	2024-12-12	2024223	{"Marcos Tadeu Pereira"}	VINCULATED_PRACTIC	33	33	6	f	f	f	f	f	2024-08-02 19:15:49.620891	128
328	2024-08-05	2024-12-12	2024224	{""}	VINCULATED_PRACTIC	31	31	0	f	f	f	f	f	2024-08-02 19:15:49.620891	128
329	2024-08-05	2024-12-12	2024231	{"Fernando Luiz Sacomano Filho"}	VINCULATED_PRACTIC	29	29	2	f	f	f	f	f	2024-08-02 19:15:49.620891	128
330	2024-08-05	2024-12-12	2024232	{"Ali Allahyarzadeh Bidgoli"}	VINCULATED_PRACTIC	29	36	1	f	f	f	f	f	2024-08-02 19:15:49.620891	128
331	2024-08-05	2024-12-12	2024241	{"Ali Allahyarzadeh Bidgoli"}	VINCULATED_PRACTIC	28	14	2	f	f	f	f	f	2024-08-02 19:15:49.620891	128
332	2024-08-05	2024-12-12	2024243	{"Ali Allahyarzadeh Bidgoli"}	VINCULATED_PRACTIC	6	6	2	f	f	f	f	f	2024-08-02 19:15:49.620891	128
333	2024-08-05	2024-12-12	2024251	{"Bruno Souza Carmo"}	VINCULATED_PRACTIC	6	6	0	f	f	f	f	f	2024-08-02 19:15:49.620891	128
334	2024-08-05	2024-12-12	2024252	{"Bruno Souza Carmo"}	VINCULATED_PRACTIC	28	21	2	f	f	f	f	f	2024-08-02 19:15:49.620891	128
335	2024-08-05	2024-12-12	2024253	{"Bruno Souza Carmo"}	VINCULATED_PRACTIC	28	31	0	f	f	f	f	f	2024-08-02 19:15:49.620891	128
336	2024-08-05	2024-12-12	2024261	{"Humberto de Camargo Gissoni"}	VINCULATED_PRACTIC	29	24	0	f	f	f	f	f	2024-08-02 19:15:49.620891	128
337	2024-08-05	2024-12-12	2024262	{"Humberto de Camargo Gissoni"}	VINCULATED_PRACTIC	6	6	2	f	f	f	f	f	2024-08-02 19:15:49.620891	128
338	2024-08-05	2024-12-12	2024264	{"Humberto de Camargo Gissoni"}	VINCULATED_PRACTIC	27	31	1	f	f	f	f	f	2024-08-02 19:15:49.620891	128
339	2024-08-05	2024-12-12	2024265	{"Alberto Hernandez Neto"}	VINCULATED_PRACTIC	20	20	5	f	f	f	f	f	2024-08-02 19:15:49.620891	128
340	2024-08-05	2024-12-12	2024267	{"Alberto Hernandez Neto"}	VINCULATED_PRACTIC	26	26	2	f	f	f	f	f	2024-08-02 19:15:49.620891	128
310	2024-08-05	2024-12-12	2024232	{"Francisco José Profito","Juliane Ribeiro da Cruz Alves"}	VINCULATED_PRACTIC	21	22	0	f	f	f	f	f	2024-08-02 19:15:49.620891	124
311	2024-08-05	2024-12-12	2024261	{"(R) Marcelo Augusto Leal Alves","Francisco José Profito","Juliane Ribeiro da Cruz Alves"}	VINCULATED_PRACTIC	20	20	1	f	f	f	f	f	2024-08-02 19:15:49.620891	124
312	2024-08-05	2024-12-12	2024262	{"(R) Marcelo Augusto Leal Alves","Francisco José Profito","Juliane Ribeiro da Cruz Alves"}	VINCULATED_PRACTIC	20	20	0	f	f	f	f	f	2024-08-02 19:15:49.620891	124
317	2024-08-05	2024-12-12	2024201	{"(R) José Roberto Simões Moreira"}	VINCULATED_THEORIC	46	37	0	f	f	f	f	f	2024-08-02 19:15:49.620891	127
318	2024-08-05	2024-12-12	2024202	{"","Guenther Carlos Krieger Filho"}	VINCULATED_THEORIC	46	44	2	f	f	f	f	f	2024-08-02 19:15:49.620891	127
319	2024-08-05	2024-12-12	2024221	{"Ernani Vitillo Volpe"}	VINCULATED_PRACTIC	23	22	0	f	f	f	f	f	2024-08-02 19:15:49.620891	127
320	2024-08-05	2024-12-12	2024222	{"Ernani Vitillo Volpe"}	VINCULATED_PRACTIC	23	15	0	f	f	f	f	f	2024-08-02 19:15:49.620891	127
321	2024-08-05	2024-12-12	2024241	{"Arlindo Tribess"}	VINCULATED_PRACTIC	22	22	1	f	f	f	f	f	2024-08-02 19:15:49.620891	127
322	2024-08-05	2024-12-12	2024242	{"Arlindo Tribess"}	VINCULATED_PRACTIC	24	22	1	f	f	f	f	f	2024-08-02 19:15:49.620891	127
342	2024-08-05	2024-12-12	2024201	{"(R) Jorge Luis Baliño"}	THEORIC	70	70	2	f	f	f	f	f	2024-08-02 19:15:49.620891	130
343	2024-08-05	2024-12-12	2024202	{"(R) Jorge Luis Baliño"}	THEORIC	70	69	3	f	f	f	f	f	2024-08-02 19:15:49.620891	130
344	2024-08-05	2024-12-12	2024203	{"(R) Jorge Luis Baliño"}	THEORIC	70	65	2	f	f	f	f	f	2024-08-02 19:15:49.620891	130
345	2024-08-05	2024-12-12	2024201	{"(R) Silvio de Oliveira Junior"}	THEORIC	120	75	1	f	f	f	f	f	2024-08-02 19:15:49.620891	131
346	2024-08-05	2024-12-12	2024201	{"(R) Marcelo Augusto Leal Alves"}	THEORIC	72	73	0	f	f	f	f	f	2024-08-02 19:15:49.620891	132
347	2024-08-05	2024-12-12	2024201	{"Marlon Sproesser Mathias"}	THEORIC	70	71	24	f	f	f	f	f	2024-08-02 19:15:49.620891	135
348	2024-08-05	2024-12-12	2024202	{"(R) Maurício Silva Ferreira"}	THEORIC	66	65	7	f	f	f	f	f	2024-08-02 19:15:49.620891	135
349	2024-08-05	2024-12-12	2024201	{"Flavio Celso Trigo"}	THEORIC	50	42	0	f	f	f	f	f	2024-08-02 19:15:49.620891	136
350	2024-08-05	2024-12-12	2024202	{"Renato Maia Matarazzo Orsino"}	THEORIC	51	38	0	f	f	f	f	f	2024-08-02 19:15:49.620891	136
351	2024-08-05	2024-12-12	2024231	{"(R) Edilson Hiroshi Tamai"}	PRACTIC	20	17	0	f	f	f	f	f	2024-08-02 19:15:49.620891	137
352	2024-08-05	2024-12-12	2024232	{"(R) Edilson Hiroshi Tamai"}	PRACTIC	20	5	0	f	f	f	f	f	2024-08-02 19:15:49.620891	137
353	2024-08-05	2024-12-12	2024241	{"(R) Flavio Celso Trigo"}	PRACTIC	21	21	1	f	f	f	f	f	2024-08-02 19:15:49.620891	137
354	2024-08-05	2024-12-12	2024242	{"(R) Flavio Celso Trigo"}	PRACTIC	20	16	1	f	f	f	f	f	2024-08-02 19:15:49.620891	137
355	2024-08-05	2024-12-12	2024221	{"(R) Roberto Spinola Barbosa","(R) Walter Jorge Augusto Ponge Ferreira","Francisco Emilio Baccaro Nigro"}	PRACTIC	29	29	22	f	f	f	f	f	2024-08-02 19:15:49.620891	138
356	2024-08-05	2024-12-12	2024251	{"(R) Roberto Spinola Barbosa","(R) Walter Jorge Augusto Ponge Ferreira","Francisco Emilio Baccaro Nigro"}	PRACTIC	33	33	32	f	f	f	f	f	2024-08-02 19:15:49.620891	138
357	2024-08-05	2024-12-12	2024201	{"(R) Roberto Martins de Souza","Juliane Ribeiro da Cruz Alves"}	THEORIC	84	54	1	f	f	f	f	f	2024-08-02 19:15:49.620891	139
358	2024-08-05	2024-12-12	2024221	{"(R) Marcelo Augusto Leal Alves"}	THEORIC	40	21	0	f	f	f	f	f	2024-08-02 19:15:49.620891	140
359	2024-08-05	2024-12-12	2024222	{"(R) Marcelo Augusto Leal Alves"}	THEORIC	40	38	1	f	f	f	f	f	2024-08-02 19:15:49.620891	140
360	2024-08-05	2024-12-12	2024201	{"(R) Jurandir Itizo Yanagihara","Fernando Luiz Sacomano Filho"}	VINCULATED_THEORIC	82	70	1	f	f	f	f	f	2024-08-02 19:15:49.620891	141
361	2024-08-05	2024-12-12	2024231	{"(R) Arlindo Tribess"}	VINCULATED_PRACTIC	21	14	0	f	f	f	f	f	2024-08-02 19:15:49.620891	141
362	2024-08-05	2024-12-12	2024232	{"(R) Arlindo Tribess"}	VINCULATED_PRACTIC	20	18	0	f	f	f	f	f	2024-08-02 19:15:49.620891	141
363	2024-08-05	2024-12-12	2024251	{"(R) Flávio Augusto Sanzovo Fiorelli"}	VINCULATED_PRACTIC	17	15	0	f	f	f	f	f	2024-08-02 19:15:49.620891	141
364	2024-08-05	2024-12-12	2024252	{"(R) Flávio Augusto Sanzovo Fiorelli"}	VINCULATED_PRACTIC	24	23	1	f	f	f	f	f	2024-08-02 19:15:49.620891	141
365	2024-08-05	2024-12-12	2024201	{"(R) Guenther Carlos Krieger Filho"}	THEORIC	75	55	3	f	f	f	f	f	2024-08-02 19:15:49.620891	142
366	2024-08-05	2024-12-12	2024201	{"(R) Raúl González Lima"}	THEORIC	81	68	1	f	f	f	f	f	2024-08-02 19:15:49.620891	143
367	2024-08-05	2024-12-12	2024201	{"(R) Paulo Carlos Kaminski"}	THEORIC	70	29	0	f	f	f	f	f	2024-08-02 19:15:49.620891	144
368	2024-08-05	2024-12-12	2024201	{"(R) Alberto Hernandez Neto"}	THEORIC	70	54	1	f	f	f	f	f	2024-08-02 19:15:49.620891	145
369	2024-08-05	2024-12-12	2024201	{"(R) Alberto Hernandez Neto"}	THEORIC	80	71	45	f	f	f	f	f	2024-08-02 19:15:49.620891	146
370	2024-08-05	2024-12-12	2024201	{"(R) Roberto Ramos Junior"}	THEORIC	33	13	0	f	f	f	f	f	2024-08-02 19:15:49.620891	147
371	2024-08-05	2024-12-12	2024201	{"(R) Fábio Saltara"}	THEORIC	30	8	0	f	f	f	f	f	2024-08-02 19:15:49.620891	148
372	2024-08-05	2024-12-12	2024201	{"Marlon Sproesser Mathias"}	THEORIC	30	12	0	f	f	f	f	f	2024-08-02 19:15:49.620891	149
373	2024-08-05	2024-12-12	2024201	{"Marcelo Augusto Leal Alves"}	THEORIC	31	15	1	f	f	f	f	f	2024-08-02 19:15:49.620891	150
374	2024-08-05	2024-12-12	2024201	{"(R) Leandro Vieira da Silva Macedo"}	THEORIC	31	16	1	f	f	f	f	f	2024-08-02 19:15:49.620891	151
375	2024-08-05	2024-12-12	2024201	{"(R) Bruno Souza Carmo","(R) Demetrio Cornilios Zachariadis"}	THEORIC	41	18	0	f	f	f	f	f	2024-08-02 19:15:49.620891	152
376	2024-08-05	2024-12-12	2024231	{"(R) José Roberto Simões Moreira","André Luiz Veiga Gimenes","Jose Aquiles Baesso Grimoni"}	PRACTIC	15	5	0	f	f	f	f	f	2024-08-02 19:15:49.620891	153
377	2024-08-05	2024-12-12	2024232	{"(R) José Roberto Simões Moreira","André Luiz Veiga Gimenes","Jose Aquiles Baesso Grimoni"}	PRACTIC	15	3	0	f	f	f	f	f	2024-08-02 19:15:49.620891	153
378	2024-08-05	2024-12-12	2024252	{"(R) José Roberto Simões Moreira","André Luiz Veiga Gimenes","Jose Aquiles Baesso Grimoni"}	PRACTIC	16	12	0	f	f	f	f	f	2024-08-02 19:15:49.620891	153
379	2024-08-05	2024-12-12	2024201	{"(R) Raúl González Lima"}	THEORIC	21	13	0	f	f	f	f	f	2024-08-02 19:15:49.620891	154
380	2024-08-05	2024-12-12	2024201	{"(R) Antonio Luis de Campos Mariani"}	THEORIC	25	15	1	f	f	f	f	f	2024-08-02 19:15:49.620891	155
381	2024-08-05	2024-12-12	2024202	{"Marlon Sproesser Mathias"}	THEORIC	25	3	0	f	f	f	f	f	2024-08-02 19:15:49.620891	155
382	2024-08-05	2024-12-12	2024201	{"(R) Julio Romano Meneghini"}	THEORIC	25	25	0	f	f	f	f	f	2024-08-02 19:15:49.620891	156
383	2024-08-05	2024-12-12	2024201	{"(R) Marcelo Augusto Leal Alves"}	THEORIC	15	3	0	f	f	f	f	f	2024-08-02 19:15:49.620891	157
384	2024-08-05	2024-12-12	2024202	{"(R) Antonio Luis de Campos Mariani"}	THEORIC	15	2	0	f	f	f	f	f	2024-08-02 19:15:49.620891	157
385	2024-08-05	2024-12-11	2024250	{"(R) Anna Luiza Marques Ayres da Silva"}	THEORIC	43	13	0	f	f	f	f	f	2024-08-02 19:15:49.620891	159
386	2024-08-05	2024-12-11	2024250	{"(R) Luis Enrique Sánchez","(R) Manoel Rodrigues Neves"}	THEORIC	60	23	2	f	f	f	f	f	2024-08-02 19:15:49.620891	160
387	2024-08-05	2024-12-12	2024290	{"(R) Elsa Vásquez Alvarez"}	THEORIC	30	4	0	f	f	f	f	f	2024-08-02 19:15:49.620891	161
388	2024-08-05	2024-12-12	2024290	{"(R) Cleyton de Carvalho Carneiro","(R) Rafael dos Santos Gioria"}	THEORIC	25	7	0	f	f	f	f	f	2024-08-02 19:15:49.620891	162
389	2024-08-05	2024-12-12	2024290	{"Elsa Vásquez Alvarez"}	THEORIC	60	60	0	f	f	f	f	f	2024-08-02 19:15:49.620891	163
390	2024-08-05	2024-12-11	2024250	{"(R) Giorgio Francesco Cesare de Tomi","(R) Ricardo Cabral de Azevedo"}	THEORIC	51	9	0	f	f	f	f	f	2024-08-02 19:15:49.620891	164
391	2024-08-05	2024-12-11	2024251	{"(R) Eduardo Cesar Sansone"}	THEORIC	72	57	1	f	f	f	f	f	2024-08-02 19:15:49.620891	165
392	2024-08-05	2024-12-11	2024250	{"(R) Anna Luiza Marques Ayres da Silva","Ana Carolina Russo"}	THEORIC	51	39	1	f	f	f	f	f	2024-08-02 19:15:49.620891	166
393	2024-08-05	2024-12-11	2024250	{"(R) Anna Luiza Marques Ayres da Silva","Ana Carolina Russo"}	THEORIC	72	52	0	f	f	f	f	f	2024-08-02 19:15:49.620891	167
396	2024-08-05	2024-12-11	2024250	{"(R) Jose Renato Baptista de Lima","Arthur Pinto Chaves"}	THEORIC	25	17	0	f	f	f	f	f	2024-08-02 19:15:49.620891	170
397	2024-08-05	2024-12-11	2024250	{"(R) Giorgio Francesco Cesare de Tomi","(R) Ricardo Cabral de Azevedo"}	THEORIC	69	12	0	f	f	f	f	f	2024-08-02 19:15:49.620891	171
398	2024-08-05	2024-12-11	2024250	{"(R) Maurício Guimarães Bergerman"}	THEORIC	60	10	0	f	f	f	f	f	2024-08-02 19:15:49.620891	172
399	2024-08-05	2024-12-12	2024290	{"(R) Eduardo Cesar Sansone"}	THEORIC	54	14	0	f	f	f	f	f	2024-08-02 19:15:49.620891	173
400	2024-08-05	2024-12-11	2024250	{"(R) Wilson Siguemasa Iramina"}	THEORIC	55	13	0	f	f	f	f	f	2024-08-02 19:15:49.620891	174
401	2024-08-05	2024-12-11	2024250	{"(R) Luis Enrique Sánchez"}	THEORIC	65	16	0	f	f	f	f	f	2024-08-02 19:15:49.620891	175
402	2024-08-05	2024-12-11	2024250	{"(R) Manoel Rodrigues Neves"}	THEORIC	60	15	1	f	f	f	f	f	2024-08-02 19:15:49.620891	176
407	2024-08-05	2024-12-11	2024250	{"(R) Luis Enrique Sánchez","Juliana Siqueira Gay"}	THEORIC	82	64	2	f	f	f	f	f	2024-08-02 19:15:49.620891	182
409	2024-08-05	2024-12-11	2024201	{"(R) Carina Ulsen","Jean Vicente Ferrari"}	THEORIC	80	26	0	f	f	f	f	f	2024-08-02 19:15:49.620891	184
410	2024-08-05	2024-12-11	2024202	{"(R) Carina Ulsen","Jean Vicente Ferrari"}	THEORIC	67	63	0	f	f	f	f	f	2024-08-02 19:15:49.620891	184
414	2024-08-05	2024-12-12	2024290	{"Nara Angélica Policarpo"}	THEORIC	46	13	0	f	f	f	f	f	2024-08-02 19:15:49.620891	188
394	2024-08-05	2024-12-12	2024290	{"Rafael dos Santos Gioria"}	THEORIC	32	7	1	f	f	f	f	f	2024-08-02 19:15:49.620891	168
395	2024-08-05	2024-12-11	2024250	{"(R) Laurindo de Salles Leal Filho"}	THEORIC	49	7	0	f	f	f	f	f	2024-08-02 19:15:49.620891	169
403	2024-08-05	2024-12-12	2024290	{"(R) Patricia Helena Lara dos Santos Matai"}	THEORIC	56	11	0	f	f	f	f	f	2024-08-02 19:15:49.620891	177
404	2024-08-05	2024-12-12	2024290	{"(R) Patricia Helena Lara dos Santos Matai"}	THEORIC	56	9	0	f	f	f	f	f	2024-08-02 19:15:49.620891	178
405	2024-08-05	2024-12-11	2024250	{"(R) Carina Ulsen","(R) Maurício Guimarães Bergerman"}	THEORIC	40	13	1	f	f	f	f	f	2024-08-02 19:15:49.620891	179
406	2024-08-05	2024-12-11	2024250	{"(R) Jose Renato Baptista de Lima"}	THEORIC	45	3	1	f	f	f	f	f	2024-08-02 19:15:49.620891	180
408	2024-08-05	2024-12-11	2024250	{"(R) Luis Enrique Sánchez"}	THEORIC	61	27	0	f	f	f	f	f	2024-08-02 19:15:49.620891	183
411	2024-08-05	2024-12-11	2024250	{"(R) Giorgio Francesco Cesare de Tomi"}	THEORIC	56	20	0	f	f	f	f	f	2024-08-02 19:15:49.620891	185
412	2024-08-05	2024-12-12	2024290	{"Gleison Elias da Silva"}	PRACTIC	50	11	0	f	f	f	f	f	2024-08-02 19:15:49.620891	186
415	2024-08-05	2024-12-11	2024250	{"(R) Eduardo Cesar Sansone"}	THEORIC	53	22	1	f	f	f	f	f	2024-08-02 19:15:49.620891	189
416	2024-08-05	2024-12-11	2024250	{"(R) Eduardo Cesar Sansone","(R) Wilson Siguemasa Iramina"}	THEORIC	51	27	0	f	f	f	f	f	2024-08-02 19:15:49.620891	190
417	2024-08-05	2024-12-11	2024250	{"(R) Homero Delboni Junior"}	THEORIC	52	21	1	f	f	f	f	f	2024-08-02 19:15:49.620891	191
418	2024-08-05	2024-12-11	2024250	{"(R) Ana Carolina Chieregati"}	THEORIC	14	15	0	f	f	f	f	f	2024-08-02 19:15:49.620891	192
419	2024-08-05	2024-12-12	2024290	{"(R) Cleyton de Carvalho Carneiro"}	THEORIC	44	14	0	f	f	f	f	f	2024-08-02 19:15:49.620891	193
420	2024-08-05	2024-12-12	2024290	{"(R) Nara Angélica Policarpo"}	THEORIC	46	11	0	f	f	f	f	f	2024-08-02 19:15:49.620891	194
421	2024-08-05	2024-12-12	2024290	{"(R) Nara Angélica Policarpo"}	THEORIC	46	10	0	f	f	f	f	f	2024-08-02 19:15:49.620891	195
422	2024-08-05	2024-12-12	2024290	{"Regina Meyer Branski"}	THEORIC	44	10	0	f	f	f	f	f	2024-08-02 19:15:49.620891	196
423	2024-08-05	2024-12-12	2024290	{"(R) Ricardo Cabral de Azevedo"}	THEORIC	46	12	0	f	f	f	f	f	2024-08-02 19:15:49.620891	197
424	2024-08-05	2024-12-12	2024290	{"(R) Ricardo Cabral de Azevedo"}	THEORIC	44	10	0	f	f	f	f	f	2024-08-02 19:15:49.620891	198
425	2024-08-05	2024-12-12	2024290	{"(R) Nara Angélica Policarpo"}	THEORIC	33	10	0	f	f	f	f	f	2024-08-02 19:15:49.620891	199
413	2024-08-05	2024-12-11	2024250	{"(R) Jose Renato Baptista de Lima"}	THEORIC	45	8	0	f	f	f	f	f	2024-08-02 19:15:49.620891	187
426	2024-08-05	2024-12-12	2024290	{"Rafael dos Santos Gioria"}	THEORIC	44	16	0	f	f	f	f	f	2024-08-02 19:15:49.620891	200
427	2024-08-05	2024-12-12	2024290	{"(R) Elsa Vásquez Alvarez"}	THEORIC	32	24	0	f	f	f	f	f	2024-08-02 19:15:49.620891	201
428	2024-08-05	2024-12-12	2024290	{"(R) Rafael dos Santos Gioria"}	THEORIC	46	20	0	f	f	f	f	f	2024-08-02 19:15:49.620891	202
429	2024-08-05	2024-12-12	2024290	{"(R) Rafael dos Santos Gioria"}	THEORIC	46	14	0	f	f	f	f	f	2024-08-02 19:15:49.620891	203
430	2024-08-05	2024-12-12	2024201	{"Martin Paul Schwark"}	THEORIC	85	73	2	f	f	f	f	f	2024-08-02 19:15:49.620891	205
431	2024-08-05	2024-12-12	2024202	{"Pedro Afonso de Oliveira Almeida"}	THEORIC	86	68	0	f	f	f	f	f	2024-08-02 19:15:49.620891	205
432	2024-08-05	2024-12-12	2024250	{"Joaquin Ignacio Bonnecarrere Garcia"}	THEORIC	41	26	0	f	f	f	f	f	2024-08-02 19:15:49.620891	206
433	2024-08-05	2024-12-11	2024250	{"Luis Alberto Follegatti Romero"}	THEORIC	69	69	0	f	f	f	f	f	2024-08-02 19:15:49.620891	207
434	2024-08-05	2024-12-12	2024201	{"(R) Daniel Setrak Sowmy"}	THEORIC	94	90	0	f	f	f	f	f	2024-08-02 19:15:49.620891	209
435	2024-08-05	2024-12-12	2024201	{"Marcelo Schneck de Paula Pessoa"}	THEORIC	72	45	0	f	f	f	f	f	2024-08-02 19:15:49.620891	210
436	2024-08-05	2024-12-12	2024201	{"(R) Ettore Jose Bottura","(R) Felipe Issa Kabbach Junior"}	VINCULATED_THEORIC	49	46	0	f	f	f	f	f	2024-08-02 19:15:49.620891	211
437	2024-08-05	2024-12-12	2024202	{"Laura Nascimento Mazzoni","Rosângela dos Santos Motta"}	VINCULATED_THEORIC	47	39	0	f	f	f	f	f	2024-08-02 19:15:49.620891	211
438	2024-08-05	2024-12-12	2024211	{"(R) Ettore Jose Bottura"}	VINCULATED_PRACTIC	49	46	0	f	f	f	f	f	2024-08-02 19:15:49.620891	211
439	2024-08-05	2024-12-12	2024221	{"(R) Felipe Issa Kabbach Junior","Laura Nascimento Mazzoni"}	VINCULATED_PRACTIC	47	39	0	f	f	f	f	f	2024-08-02 19:15:49.620891	211
440	2024-08-05	2024-12-12	2024201	{"(R) José Carlos Mierzwa"}	THEORIC	45	43	0	f	f	f	f	f	2024-08-02 19:15:49.620891	212
441	2024-08-05	2024-12-12	2024202	{"(R) Sidney Seckler Ferreira Filho"}	THEORIC	45	41	0	f	f	f	f	f	2024-08-02 19:15:49.620891	212
442	2024-08-05	2024-12-12	2024201	{"(R) Eliane Monetti"}	THEORIC	42	42	1	f	f	f	f	f	2024-08-02 19:15:49.620891	213
443	2024-08-05	2024-12-12	2024202	{"(R) Claudio Tavares de Alencar"}	THEORIC	42	25	0	f	f	f	f	f	2024-08-02 19:15:49.620891	213
444	2024-08-05	2024-12-12	2024203	{"(R) Eliane Monetti"}	THEORIC	48	47	0	f	f	f	f	f	2024-08-02 19:15:49.620891	213
445	2024-08-05	2024-12-12	2024204	{"(R) Claudio Tavares de Alencar"}	THEORIC	47	42	1	f	f	f	f	f	2024-08-02 19:15:49.620891	213
446	2024-08-05	2024-12-12	2024201	{"(R) Sérgio Cirelli Angulo"}	THEORIC	30	1	0	f	f	f	f	f	2024-08-02 19:15:49.620891	214
447	2024-08-05	2024-12-12	2024250	{"(R) Amarilis Lucia Casteli Figueiredo Gallardo"}	THEORIC	50	31	1	f	f	f	f	f	2024-08-02 19:15:49.620891	215
448	2024-08-05	2024-12-12	2024201	{"(R) Luiz Reynaldo de Azevedo Cardoso"}	THEORIC	30	11	0	f	f	f	f	f	2024-08-02 19:15:49.620891	216
449	2024-08-05	2024-12-12	2024201	{"Juliana Siqueira Gay"}	THEORIC	62	47	0	f	f	f	f	f	2024-08-02 19:15:49.620891	217
450	2024-08-05	2024-12-12	2024202	{"Rachel Biancalana Costa"}	THEORIC	63	62	1	f	f	f	f	f	2024-08-02 19:15:49.620891	217
451	2024-08-05	2024-12-12	2024203	{"Sidney Seckler Ferreira Filho"}	THEORIC	59	59	0	f	f	f	f	f	2024-08-02 19:15:49.620891	217
452	2024-08-05	2024-12-12	2024204	{"(R) Monica Ferreira do Amaral Porto"}	THEORIC	65	65	1	f	f	f	f	f	2024-08-02 19:15:49.620891	217
453	2024-08-05	2024-12-12	2024206	{"Arisvaldo Vieira Mello Júnior"}	THEORIC	50	39	10	f	f	f	f	f	2024-08-02 19:15:49.620891	217
454	2024-08-05	2024-12-12	2024201	{"(R) Joseph Harari"}	THEORIC	64	49	0	f	f	f	f	f	2024-08-02 19:15:49.620891	218
455	2024-08-05	2024-12-12	2024202	{"Henrique de Britto Costa"}	THEORIC	58	43	0	f	f	f	f	f	2024-08-02 19:15:49.620891	108
\.


--
-- TOC entry 3218 (class 0 OID 25124)
-- Dependencies: 222
-- Data for Name: classcalendarlink; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.classcalendarlink (class_id, calendar_id) FROM stdin;
238	1
\.


--
-- TOC entry 3220 (class 0 OID 25141)
-- Dependencies: 224
-- Data for Name: classroom; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.classroom (name, capacity, floor, ignore_to_allocate, accessibility, projector, air_conditioning, updated_at, created_by_id, building_id, id) FROM stdin;
CT-04	75	0	f	t	t	t	2024-07-31 22:04:12.455258	5	1	1
C1-04	85	1	f	f	t	t	2024-07-31 22:04:12.455258	5	1	3
C1-05	85	1	f	f	t	t	2024-07-31 22:04:12.455258	5	1	4
C1-09	85	1	f	f	t	t	2024-07-31 22:04:12.455258	5	1	5
C2-01	85	2	f	f	t	t	2024-08-01 00:44:31.462588	5	1	6
C2-03	85	2	f	f	t	t	2024-08-01 00:45:33.018674	5	1	7
C1-03	85	1	f	f	t	t	2024-08-01 00:46:04.176847	5	1	2
C2-02	85	2	f	f	t	t	2024-07-31 22:04:12.455258	5	1	8
C2-04	85	2	f	f	t	t	2024-07-31 22:04:12.455258	5	1	9
C2-05	85	2	f	f	t	t	2024-07-31 22:04:12.455258	5	1	10
C2-06	85	2	f	f	t	t	2024-07-31 22:04:12.455258	5	1	11
C2-07	85	2	f	f	t	t	2024-07-31 22:04:12.455258	5	1	12
C2-08	85	2	f	f	t	t	2024-07-31 22:04:12.455258	5	1	13
C2-09	85	2	f	f	t	t	2024-07-31 22:04:12.455258	5	1	14
C2-13	85	2	f	f	t	t	2024-07-31 22:04:12.455258	5	1	15
A1-01	95	1	f	t	f	t	2024-07-31 22:04:12.455258	5	1	16
A1-02	95	1	f	t	f	t	2024-07-31 22:04:12.455258	5	1	17
A1-03	95	1	f	t	f	t	2024-07-31 22:04:12.455258	5	1	18
A1-04	95	1	f	t	f	t	2024-07-31 22:04:12.455258	5	1	19
A1-05	95	1	f	t	f	t	2024-07-31 22:04:12.455258	5	1	20
B2-01	60	1	f	f	f	f	2024-07-31 22:04:12.455258	5	2	21
B2-03	58	1	f	t	f	t	2024-07-31 22:04:12.455258	5	2	22
B2-04	56	1	f	t	f	t	2024-07-31 22:04:12.455258	5	2	23
B2-05	66	1	f	t	f	t	2024-07-31 22:04:12.455258	5	2	24
B2-06	55	1	f	t	f	t	2024-07-31 22:04:12.455258	5	2	25
B2-09	60	1	f	t	f	t	2024-07-31 22:04:12.455258	5	2	26
B2-10	55	1	f	t	f	t	2024-07-31 22:04:12.455258	5	2	27
A1-10	50	0	f	t	f	t	2024-07-31 22:04:12.455258	5	2	28
C1-38	27	0	f	t	t	t	2024-07-31 22:04:12.455258	5	2	29
D1-01	100	0	f	t	f	t	2024-07-31 22:04:12.455258	5	2	30
D1-02	100	0	f	t	f	t	2024-07-31 22:04:12.455258	5	2	31
D1-03	100	0	f	t	f	t	2024-07-31 22:04:12.455258	5	2	32
D1-04	100	0	f	t	f	t	2024-07-31 22:04:12.455258	5	2	33
GD-07	55	0	f	t	f	t	2024-07-31 22:04:12.455258	5	2	34
LabSoft	50	0	f	t	f	t	2024-07-31 22:04:12.455258	5	2	36
Pró-Aluno	100	0	f	t	f	f	2024-07-31 22:04:12.455258	5	2	37
D1-01	100	0	f	f	f	f	2024-07-31 22:04:12.455258	5	3	40
D1-02	100	0	f	f	f	f	2024-07-31 22:04:12.455258	5	3	41
D1-03	100	0	f	f	f	f	2024-07-31 22:04:12.455258	5	3	42
Lab Ocean	100	0	f	f	f	f	2024-07-31 22:04:12.455258	5	3	43
ON	100	0	f	f	t	t	2024-07-31 22:04:12.455258	5	3	44
S01	80	1	f	f	t	t	2024-07-31 22:04:12.455258	5	4	45
S03	81	1	f	f	t	t	2024-07-31 22:04:12.455258	5	4	46
S04	130	1	f	f	t	t	2024-07-31 22:04:12.455258	5	4	47
S05	83	1	f	f	t	t	2024-07-31 22:04:12.455258	5	4	48
S06	120	1	f	f	t	t	2024-07-31 22:04:12.455258	5	4	49
S08	120	1	f	f	t	t	2024-07-31 22:04:12.455258	5	4	50
S09	60	1	f	f	t	t	2024-07-31 22:04:12.455258	5	4	51
S10	82	1	f	f	t	t	2024-07-31 22:04:12.455258	5	4	52
S11	60	1	f	f	t	t	2024-07-31 22:04:12.455258	5	4	53
S12	70	1	f	f	t	t	2024-07-31 22:04:12.455258	5	4	54
S13	60	1	f	f	t	t	2024-07-31 22:04:12.455258	5	4	55
S14	72	1	f	f	t	t	2024-07-31 22:04:12.455258	5	4	56
S15	50	1	f	f	t	t	2024-07-31 22:04:12.455258	5	4	57
S18	40	1	f	f	t	t	2024-07-31 22:04:12.455258	5	4	58
S19	50	1	f	f	t	t	2024-07-31 22:04:12.455258	5	4	59
S20	40	1	f	f	t	t	2024-07-31 22:04:12.455258	5	4	60
S21	50	1	f	f	t	t	2024-07-31 22:04:12.455258	5	4	61
S22	121	1	f	f	t	t	2024-07-31 22:04:12.455258	5	4	62
S26	121	1	f	f	t	t	2024-07-31 22:04:12.455258	5	4	63
S24	130	1	f	f	t	t	2024-07-31 22:04:12.455258	5	4	64
GD-06	55	0	f	t	f	t	2024-07-31 22:04:12.455258	5	2	65
A1-22	50	0	f	t	f	t	2024-07-31 22:04:12.455258	5	2	66
B2-12	56	1	f	t	f	t	2024-08-01 20:55:41.767458	5	2	35
A2-37	50	2	f	t	f	t	2024-07-31 22:04:12.455258	5	2	67
C1-30	100	0	f	t	t	f	2024-08-01 21:04:53.18968	5	2	38
C1-05	30	0	f	t	t	t	2024-08-01 21:04:57.5249	5	2	39
Remoto	1000	0	t	f	f	f	2024-07-31 22:04:12.455258	5	2	68
A1-06	95	1	f	t	f	t	2024-08-02 19:15:49.639566	5	1	69
Bloco 21 - Piso Superior Sala 17	0	0	f	f	f	f	2024-08-03 18:47:20.679385	5	7	70
Bloco 21 - Piso Superior Sala 1/3	0	0	f	f	f	f	2024-08-02 19:15:49.639566	5	7	71
C1-14	30	0	f	t	t	t	2024-08-02 19:15:49.639566	5	2	72
Auditório LARC	50	0	f	t	t	t	2024-08-02 19:15:49.639566	5	2	73
GD-04	55	0	f	t	f	t	2024-08-02 19:15:49.639566	5	2	74
B2-08	60	1	f	t	f	t	2024-08-02 19:15:49.639566	5	2	75
A-2	50	0	f	t	t	t	2024-08-02 19:15:49.639566	5	6	76
A-6	50	0	f	t	t	t	2024-08-02 19:15:49.639566	5	6	77
A-1A	50	0	f	t	t	t	2024-08-02 19:15:49.639566	5	6	78
A-8	50	0	f	t	t	t	2024-08-02 19:15:49.639566	5	6	79
A-7	50	0	f	t	t	t	2024-08-02 19:15:49.639566	5	6	80
A-9	50	0	f	t	t	t	2024-08-02 19:15:49.639566	5	6	81
A-10	50	0	f	t	t	t	2024-08-02 19:15:49.639566	5	6	82
A-3	50	0	f	t	t	t	2024-08-02 19:15:49.639566	5	6	83
A-10A	50	0	f	t	t	t	2024-08-02 19:15:49.639566	5	6	84
TS-9	50	1	f	f	t	t	2024-08-02 19:15:49.639566	5	6	85
PNV	50	0	f	f	t	t	2024-08-02 19:15:49.639566	5	6	86
Sala 01	50	0	f	f	t	t	2024-08-02 19:15:49.639566	5	8	87
Sala 02	50	0	f	f	t	t	2024-08-02 19:15:49.639566	5	8	88
Sala 03	50	0	f	f	t	t	2024-08-02 19:15:49.639566	5	8	89
Sala 04	50	0	f	f	t	t	2024-08-02 19:15:49.639566	5	8	90
Sala 05	50	0	f	f	t	t	2024-08-02 19:15:49.639566	5	8	91
Sala 06	50	0	f	f	t	t	2024-08-02 19:15:49.639566	5	8	92
Sala 07	50	0	f	f	t	t	2024-08-02 19:15:49.639566	5	8	93
\.


--
-- TOC entry 3214 (class 0 OID 25078)
-- Dependencies: 218
-- Data for Name: comment; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.comment (id, comment, email, created_by_id, created_at) FROM stdin;
1	Teste comentário do simulator iOS novo backend\t	\N	\N	2024-08-02 19:15:49.713367
2	Teste comentário simulator iOS novo backend (logado)	\N	1	2024-08-02 19:15:49.713367
3	aryrsj	\N	\N	2024-08-02 19:15:49.713367
4	ewlwqh	\N	\N	2024-08-02 19:15:49.713367
5	Não tem as matérias do projeto piloto da engenharia elétrica, o que é uma pena porque o aplicativo é muito legal.	isadora.vital@usp.br	\N	2024-08-02 19:15:49.713367
6	hyqflu\n	hhkthk	\N	2024-08-15 14:20:56.17122
7	vijomc	gdxsol	\N	2024-09-17 14:22:38.263499
8	vijomc	hhkthk	\N	2024-09-17 14:22:38.263499
9	mpeits	ywwqye	\N	2024-09-17 14:22:38.263499
10	vijomc	huvmyo	\N	2024-10-14 14:28:56.564817
11	huvmyo	sxgtow	\N	2024-10-15 14:13:03.959842
12	I 	\N	\N	2024-10-15 14:13:03.959842
\.


--
-- TOC entry 3232 (class 0 OID 25362)
-- Dependencies: 236
-- Data for Name: forumpost; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.forumpost (id, class_id, subject_id, content, user_id, created_at, report_count, reply_of_post_id, replies_count, enabled) FROM stdin;
1	144	79	Que dia começam as aulas? 	2	2024-08-02 19:15:49.672906	1	\N	0	t
2	140	79	Acho que essa semana mesmo!	21	2024-08-02 19:15:49.672906	0	\N	0	t
3	144	79	Olá pessoal! Estou por aqui também! Aproveitem o USPolis!	29	2024-08-02 19:15:49.672906	0	\N	0	t
8	52	24	Para me antecipar aqui	2	2024-10-22 20:05:21.737931	0	7	0	t
7	52	24	Precisa entregar o relatório quando?	2	2024-10-22 20:05:01.77892	0	\N	2	t
9	52	24	Também gostaria de saber!	1	2024-10-23 17:34:16.848926	0	7	0	t
\.


--
-- TOC entry 3233 (class 0 OID 33142)
-- Dependencies: 237
-- Data for Name: forumpostreportlink; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.forumpostreportlink (forum_post_id, mobile_user_id) FROM stdin;
\.


--
-- TOC entry 3222 (class 0 OID 25185)
-- Dependencies: 226
-- Data for Name: holiday; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.holiday (id, date, updated_at, category_id, created_by_id, name) FROM stdin;
1	2024-03-25	2024-07-31 23:45:07.395489	1	5	Semana Santa
2	2024-03-26	2024-07-31 23:45:07.411118	1	5	Semana Santa
3	2024-03-27	2024-07-31 23:45:07.422455	1	5	Semana Santa
4	2024-03-28	2024-07-31 23:45:07.432738	1	5	Semana Santa
5	2024-03-29	2024-07-31 23:45:07.441852	1	5	Semana Santa
6	2024-03-30	2024-07-31 23:45:07.451512	1	5	Semana Santa
10	2024-09-02	2024-08-01 00:02:35.61888	1	5	Semana da Pátria
11	2024-09-03	2024-08-01 00:02:35.629171	1	5	Semana da Pátria
12	2024-09-04	2024-08-01 00:02:35.639964	1	5	Semana da Pátria
13	2024-09-05	2024-08-01 00:02:35.64994	1	5	Semana da Pátria
14	2024-09-06	2024-08-01 00:02:35.659293	1	5	Semana da Pátria
15	2024-09-07	2024-08-01 00:02:35.669824	1	5	Semana da Pátria
16	2024-05-30	2024-08-01 00:04:12.239027	1	5	Recesso Corpus Christi
17	2024-05-31	2024-08-01 00:04:12.249431	1	5	Recesso Corpus Christi
18	2024-06-01	2024-08-01 00:04:12.259226	1	5	Recesso Corpus Christi
26	2024-05-01	2024-08-01 00:14:26.006592	1	5	Dia do trabalho
27	2024-10-12	2024-08-01 00:15:31.246859	1	5	Nossa Senhora Aparecida
28	2024-10-28	2024-08-01 00:15:44.423392	1	5	Consagração ao Funcionário Público
29	2024-11-02	2024-08-01 00:16:51.110444	1	5	Finados
30	2024-11-15	2024-08-01 00:20:52.485885	1	5	Recesso Proclamação da República
31	2024-11-16	2024-08-01 00:21:12.371344	1	5	Recesso Proclamação da República
32	2024-11-20	2024-08-01 00:21:30.047914	1	5	Consciência Negra
\.


--
-- TOC entry 3216 (class 0 OID 25094)
-- Dependencies: 220
-- Data for Name: holidaycategory; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.holidaycategory (id, name, created_by_id) FROM stdin;
1	USP	5
\.


--
-- TOC entry 3200 (class 0 OID 24957)
-- Dependencies: 204
-- Data for Name: institutionalevent; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.institutionalevent (id, title, description, category, start, "end", location, building, classroom, external_link, likes, created_at) FROM stdin;
\.


--
-- TOC entry 3202 (class 0 OID 24968)
-- Dependencies: 206
-- Data for Name: mobileuser; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.mobileuser (id, sub, email, given_name, family_name, picture_url) FROM stdin;
1	110944557049857859000	jv.makiyama@usp.br	Jose Vitor	Martins Makiyama	https://lh3.googleusercontent.com/a/ACg8ocJRVzbPS4BFDuqIhUYdLjZbAxYnrTAxvE3reGsO_hh12QzOd0Q=s96-c
2	107489405896551798325	daniell_hy@usp.br	Daniel	Hiroki Yamashita	https://lh3.googleusercontent.com/a/ACg8ocJchu22GWnVtudI3L4Tpo2kMjDc4gK90f9A3kF5CknNQWxhiQ=s96-c
3	117672502434607253683	enzo_takao@usp.br	Enzo	 Miyazaki Takao	https://lh3.googleusercontent.com/a/ACg8ocKN_uw1MRvMZUie_344rLYDmKhhaYIaC821n-YWRo7Jem3IHg=s96-c
4	103070226726863110128	mariaeduardadlp@usp.br	Maria	 Eduarda Dantas Leite Pessoa	https://lh3.googleusercontent.com/a/ACg8ocKWaf4pDIvlgY16tO-n_QZTEre04RVFymGKanrbtfIMQb93MA=s96-c
5	102578244905278076001	brunargoulart@usp.br	Bruna	 Reno Goulart	https://lh3.googleusercontent.com/a/ACg8ocIX8d9pEtKIPHhE0bbrL6o41PWJWwUguvpQI-XhVuOOtHKR-w=s96-c
6	113583912059331355934	andreatticorego@usp.br	Andre	 Attico Rego	https://lh3.googleusercontent.com/a/ACg8ocLPLcMR-cPoG6bHzWt_4ebmSwSOLzSoRQxr7h0C3bqbf9UPk34=s96-c
7	115267455609628833902	pedro.nieto@usp.br	Pedro	 Prates Nieto	https://lh3.googleusercontent.com/a/ACg8ocKhk6zXI-c81JVdQITIJCeZkmdhETVYtC24degTK4H6lD_c3g=s96-c
8	104443116202930348388	guilhermetoledo30@usp.br	Guilherme	 Gabriel Toledo dos Santos	https://lh3.googleusercontent.com/a/ACg8ocKpM6YtoeDVI9YYWTVeyv9QLuTSNQyl6NZNL1cNfswQND5qyQ=s96-c
9	107971816256892421201	dudatreze@usp.br	Eduardo	 Santos Vieira	https://lh3.googleusercontent.com/a/ACg8ocK8q72g5Sn5xXI8sAquQA5-eoy9N2eI4-Jm5pgik8zx9d0dcA=s96-c
10	118124098726442490877	tammy.hatori@usp.br	Tammy	 Hatori Ribeiro	https://lh3.googleusercontent.com/a/ACg8ocLIYzAgNaQWZUCZT_hlTbU8SUkhoNo-9uqSqWnWvIEoiuHsjAc=s96-c
11	104812080157404085717	giovannaferreira2906@usp.br	Giovanna	 Ferreira Antonio	https://lh3.googleusercontent.com/a/ACg8ocKQVvKciiqK5fPYbabIbfLx6OEJV6OLqsmXIDSveJtRxPAiHw=s96-c
12	111089966519055843563	guilhermewillians174@usp.br	Guilherme	 Willians Celestiano	https://lh3.googleusercontent.com/a/ACg8ocK31QfBdmtOYaO0Y3JE68J3gyFUxt141cGQyme_tbY5NLFjEQ=s96-c
13	110286654370374846551	pedro.felisbino@usp.br	Pedro	 Henrique da Silva Felisbino	https://lh3.googleusercontent.com/a/ACg8ocJqZlPkm-rHQFdXin8H45JvIfMg4HkWIyveA-Hypz_3TlvOZ3A=s96-c
14	113059467937242973034	isabelabelmont@usp.br	Isabela	 Belmont Menezes	https://lh3.googleusercontent.com/a/ACg8ocLmC1SeW6iKPBL-1kpy-FOpHx-6nIFNBXZ-5H1rROszk5UXXA=s96-c
15	113190076251689840379	danielpggomes@usp.br	Daniel	 Paiva Gomes	https://lh3.googleusercontent.com/a/ACg8ocILV03DixNFu2OW_QgnIvvB2GsB9mI4m9nwRI92aBThhDtZUDM=s96-c
16	103935683884217105983	joaospiridigliozzi@usp.br	Joao	 Alckmim Camara Saquetti Spiridigliozzi	https://lh3.googleusercontent.com/a/ACg8ocJhJ6VS10gmleY2EqH4BRH0y8dtvxwitf5er6noSrgdOSRpfw=s96-c
17	105783308985393511637	gabriel_camargo@usp.br	Gabriel	 di Vanna Camargo	https://lh3.googleusercontent.com/a/ACg8ocK-OCvfJ_9YsFuy4w9J13D26Ynch-Y5xkfO5EW7asEAmktyNQ=s96-c
18	112971147555679667963	henriquewillians@usp.br	Lorenzo	 Henrique Willians da Silva Rebelo	https://lh3.googleusercontent.com/a/ACg8ocLHD7yhXNTpYz-oq8hRNOg9WhtctP22gb5qOqEUr1hPS4sr8A=s96-c
19	101616791139268356055	caua.bm720@usp.br	Caua	 Moreira Bispo Marcal	https://lh3.googleusercontent.com/a/ACg8ocLVT8XHYw4PZrj2OFKF7dT1MXs5qhRIP5GPyhCkJ-yBBMO0Wg=s96-c
20	115819028105239137711	jvferreira.g@usp.br	Joao	 Victor Ferreira Goncalves	https://lh3.googleusercontent.com/a/ACg8ocLhb7Ogm5jV_59C8zm7WggLUdBhskBgLJ5pKJCUgFr0KhW6hw=s96-c
21	104231955137525510998	renan.avila@usp.br	Renan	de Luca Avila	https://lh3.googleusercontent.com/a/ACg8ocKcHUnL1QsWbtcQmy1WwrwnTxd7WV5kCzpgjtaxh7tQxOWFN68V=s96-c
22	114859813506711085029	arthur.alencar@usp.br	Arthur	 Santos Alencar	https://lh3.googleusercontent.com/a/ACg8ocJnfsvpgO1ArO1BGUQ7EoWds6sTov-R-VfHdEMmDqpZB6OI8rk=s96-c
23	106788565680812941918	henriquealves2005@usp.br	Henrique	 Alves da Silva	https://lh3.googleusercontent.com/a/ACg8ocLnTu1VZnA_yLFL90o38TBERcvreiiFDUlpvGGLjeinAqshnA=s96-c
24	104881650211232696882	viniciussampa11@usp.br	Vinicius	Meneses Souza	https://lh3.googleusercontent.com/a/ACg8ocIVoFUFW_7EW7sfJWGQCIJvnKp0i7soD8HV9JPscGO5n-Tqxig=s96-c
25	102463634792173404916	joao_queiroz@usp.br	Joao	 Guilherme Lopes Queiroz	https://lh3.googleusercontent.com/a/ACg8ocIiyG2aA3jPHRlL_fqSofBML2tykvZlEKYZ_7mAnqK0vm5Hpdg=s96-c
26	108311271814687534974	augustopmello@usp.br	Augusto	 Henrique Pereira Mello	https://lh3.googleusercontent.com/a/ACg8ocIZ9xIrWfUhi_O5ted_FGcqEaJRdf2ISpIX73D4cqffQWmcSQ=s96-c
27	116752449045042777833	julio.moura@usp.br	Julio	 Barbosa de Moura	https://lh3.googleusercontent.com/a/ACg8ocJBb5t5WTstdIKPd2f4p6V9oNV2oNJ1uuDWQM5Qe4Q7w0tvJQ=s96-c
28	103433916616265383996	tomazfilla@usp.br	Tomaz	 Cavalcanti Fatel Filla	https://lh3.googleusercontent.com/a/ACg8ocL4YORapcdfRqWxGRroH8fVOROrcTVdkBxtKRLY1mHSlidgkQ=s96-c
29	111813088346505511873	levy.siqueira@usp.br	Fabio	Levy Siqueira	https://lh3.googleusercontent.com/a/ACg8ocJfIWy8OKiUljVTZAUHIIuvYZCixsvxPhBgtYxCwhuKemWQPyJr=s96-c
30	109244591287290143058	ggccastilho@usp.br	Gustavo	 Garcia Castilho	https://lh3.googleusercontent.com/a/ACg8ocKLL3x_mXMe-7EbVgXgyzkMGvTiL0q8Yw4qmmE0zsv9M-vz4Io=s96-c
31	103822210030512986746	vinicius.crusca@usp.br	Vinicius	 Desiderio Crusca	https://lh3.googleusercontent.com/a/ACg8ocJZ3iHvGVxuFdnrw3x_8ccnCIvl5Mk-4iFLzHWu-JMphlvT0Q=s96-c
32	115242356485860066640	guilhermeoandrade@usp.br	Guilherme	 de Oliveira Andrade	https://lh3.googleusercontent.com/a/ACg8ocKwZuADkjBmXqi_Ahtvt-ISqCXnruqHbwGB0DrYya8JLU8uvA=s96-c
33	106686238135022947198	matheus.moraesgomes@usp.br	Matheus	 de Moraes Gomes	https://lh3.googleusercontent.com/a/ACg8ocI0O7_BTc8TrCDSgmlf3SYkqOZZRJ2_YFwld8mwksUXykhUASoc=s96-c
34	102561112503785757243	mlss0205@usp.br	Maria	 Luiza Siqueira Santos	https://lh3.googleusercontent.com/a/ACg8ocKeDcZkHz5aZfEZYYMrFxe7rh2D07awcUyBKDtWVyhT6RzzFw=s96-c
35	104592806084652928798	pedrosato@usp.br	Pedro	 Sato de Aragao	https://lh3.googleusercontent.com/a/ACg8ocKLJ8GT0waOzLiU1LxYnWIuVxuenX5CbDh390wU3MH1XYLEkA=s96-c
36	113229595945310512639	joaochaar@usp.br	Joao	 Vitor Chaar da Silva	https://lh3.googleusercontent.com/a/ACg8ocIb7LA-aDuwQfToQJDjG3UVk6QkIIPI4W-Rv6rf8UZK31zLd_k=s96-c
37	113134821675101953701	andrerosales581@usp.br	Andre	 Rosales Saavedra	https://lh3.googleusercontent.com/a/ACg8ocJEscTSv5Vv2KLQoHmqApvoXcKi-e1-j9AtYtv6R8u3WkREHQ=s96-c
38	102091248584819143293	otavio.luca@usp.br	Otavio	 Maciel de Luca	https://lh3.googleusercontent.com/a/ACg8ocJWoGFK7Hvc8MUYRtl8fOSkSWceFFJ23HBGG6EMdSBZdylvOw=s96-c
39	102079299962082052017	amorimjv@usp.br	Joao	 Vitor de Amorim Paula	https://lh3.googleusercontent.com/a/ACg8ocKvBbncGaFJIHbnwJ3L9UB2ThKROsWMdZEJ986lahgBT_NYaSI=s96-c
40	103356036422145673911	marceladesiderio.md@usp.br	Marcela	 Bezerra Desiderio	https://lh3.googleusercontent.com/a/ACg8ocJK2qb24xxIFSoRvsKuCwADn-d9-HGDN0kex72OokKGmaYPvA4=s96-c
41	104780495270434398375	b.machado@usp.br	Beatriz	 Machado de Araujo	https://lh3.googleusercontent.com/a/ACg8ocJF1EYbFDbpECjcuLZuEdAf_xo1JKdtQ91W6G5XsnWCSl40smA=s96-c
42	111393484023118095704	victor-ry@usp.br	Victor	Ruan Ye	https://lh3.googleusercontent.com/a/ACg8ocIbfyEa27LCz3kllmYx6WH_FnESTsSghLYzSHd7gDUsrbNuEg=s96-c
43	110090069091171696455	aprimitz@usp.br	Alvaro	 Primitz	https://lh3.googleusercontent.com/a/ACg8ocK2Sb9tf_v7693vRRe7XsRl2HTurRVfX2WlLYhCwT3_igtXFg=s96-c
44	108607977119081293325	pedrohrs@usp.br	Pedro	 Henrique Rosa dos Santos	https://lh3.googleusercontent.com/a/ACg8ocIhIfxAyedQaExY5P4t_4tYFq_0Dg5q78eW7R8OKIfMne15Cg=s96-c
\.


--
-- TOC entry 3230 (class 0 OID 25330)
-- Dependencies: 234
-- Data for Name: occurrence; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.occurrence (id, start_time, end_time, date, classroom_id, schedule_id) FROM stdin;
1	13:10:00	14:50:00	2024-08-05	32	231
2	13:10:00	14:50:00	2024-08-12	32	231
3	13:10:00	14:50:00	2024-08-19	32	231
4	13:10:00	14:50:00	2024-08-26	32	231
5	13:10:00	14:50:00	2024-09-02	32	231
6	13:10:00	14:50:00	2024-09-09	32	231
7	13:10:00	14:50:00	2024-09-16	32	231
8	13:10:00	14:50:00	2024-09-23	32	231
9	13:10:00	14:50:00	2024-09-30	32	231
10	13:10:00	14:50:00	2024-10-07	32	231
11	13:10:00	14:50:00	2024-10-14	32	231
12	13:10:00	14:50:00	2024-10-21	32	231
13	13:10:00	14:50:00	2024-10-28	32	231
14	13:10:00	14:50:00	2024-11-04	32	231
15	13:10:00	14:50:00	2024-11-11	32	231
16	13:10:00	14:50:00	2024-11-18	32	231
17	13:10:00	14:50:00	2024-11-25	32	231
18	13:10:00	14:50:00	2024-12-02	32	231
19	13:10:00	14:50:00	2024-12-09	32	231
20	15:00:00	16:40:00	2024-08-05	38	1
21	15:00:00	16:40:00	2024-08-12	38	1
22	15:00:00	16:40:00	2024-08-19	38	1
23	15:00:00	16:40:00	2024-08-26	38	1
24	15:00:00	16:40:00	2024-09-02	38	1
25	15:00:00	16:40:00	2024-09-09	38	1
26	15:00:00	16:40:00	2024-09-16	38	1
27	15:00:00	16:40:00	2024-09-23	38	1
28	15:00:00	16:40:00	2024-09-30	38	1
29	15:00:00	16:40:00	2024-10-07	38	1
30	15:00:00	16:40:00	2024-10-14	38	1
31	15:00:00	16:40:00	2024-10-21	38	1
32	15:00:00	16:40:00	2024-10-28	38	1
33	15:00:00	16:40:00	2024-11-04	38	1
34	15:00:00	16:40:00	2024-11-11	38	1
35	15:00:00	16:40:00	2024-11-18	38	1
36	15:00:00	16:40:00	2024-11-25	38	1
37	15:00:00	16:40:00	2024-12-02	38	1
38	15:00:00	16:40:00	2024-12-09	38	1
39	15:00:00	16:40:00	2024-08-09	38	2
40	15:00:00	16:40:00	2024-08-16	38	2
41	15:00:00	16:40:00	2024-08-23	38	2
42	15:00:00	16:40:00	2024-08-30	38	2
43	15:00:00	16:40:00	2024-09-06	38	2
44	15:00:00	16:40:00	2024-09-13	38	2
45	15:00:00	16:40:00	2024-09-20	38	2
46	15:00:00	16:40:00	2024-09-27	38	2
47	15:00:00	16:40:00	2024-10-04	38	2
48	15:00:00	16:40:00	2024-10-11	38	2
49	15:00:00	16:40:00	2024-10-18	38	2
50	15:00:00	16:40:00	2024-10-25	38	2
51	15:00:00	16:40:00	2024-11-01	38	2
52	15:00:00	16:40:00	2024-11-08	38	2
53	15:00:00	16:40:00	2024-11-15	38	2
54	15:00:00	16:40:00	2024-11-22	38	2
55	15:00:00	16:40:00	2024-11-29	38	2
56	15:00:00	16:40:00	2024-12-06	38	2
57	07:30:00	11:00:00	2024-08-06	66	3
58	07:30:00	11:00:00	2024-08-13	66	3
59	07:30:00	11:00:00	2024-08-20	66	3
60	07:30:00	11:00:00	2024-08-27	66	3
61	07:30:00	11:00:00	2024-09-03	66	3
62	07:30:00	11:00:00	2024-09-10	66	3
63	07:30:00	11:00:00	2024-09-17	66	3
64	07:30:00	11:00:00	2024-09-24	66	3
65	07:30:00	11:00:00	2024-10-01	66	3
66	07:30:00	11:00:00	2024-10-08	66	3
67	07:30:00	11:00:00	2024-10-15	66	3
68	07:30:00	11:00:00	2024-10-22	66	3
69	07:30:00	11:00:00	2024-10-29	66	3
70	07:30:00	11:00:00	2024-11-05	66	3
71	07:30:00	11:00:00	2024-11-12	66	3
72	07:30:00	11:00:00	2024-11-19	66	3
73	07:30:00	11:00:00	2024-11-26	66	3
74	07:30:00	11:00:00	2024-12-03	66	3
75	07:30:00	11:00:00	2024-12-10	66	3
76	07:30:00	11:00:00	2024-08-06	66	4
77	07:30:00	11:00:00	2024-08-13	66	4
78	07:30:00	11:00:00	2024-08-20	66	4
79	07:30:00	11:00:00	2024-08-27	66	4
80	07:30:00	11:00:00	2024-09-03	66	4
81	07:30:00	11:00:00	2024-09-10	66	4
82	07:30:00	11:00:00	2024-09-17	66	4
83	07:30:00	11:00:00	2024-09-24	66	4
84	07:30:00	11:00:00	2024-10-01	66	4
85	07:30:00	11:00:00	2024-10-08	66	4
86	07:30:00	11:00:00	2024-10-15	66	4
87	07:30:00	11:00:00	2024-10-22	66	4
88	07:30:00	11:00:00	2024-10-29	66	4
89	07:30:00	11:00:00	2024-11-05	66	4
90	07:30:00	11:00:00	2024-11-12	66	4
91	07:30:00	11:00:00	2024-11-19	66	4
92	07:30:00	11:00:00	2024-11-26	66	4
93	07:30:00	11:00:00	2024-12-03	66	4
94	07:30:00	11:00:00	2024-12-10	66	4
95	13:10:00	16:40:00	2024-08-09	66	5
96	13:10:00	16:40:00	2024-08-16	66	5
97	13:10:00	16:40:00	2024-08-23	66	5
98	13:10:00	16:40:00	2024-08-30	66	5
99	13:10:00	16:40:00	2024-09-06	66	5
100	13:10:00	16:40:00	2024-09-13	66	5
101	13:10:00	16:40:00	2024-09-20	66	5
102	13:10:00	16:40:00	2024-09-27	66	5
103	13:10:00	16:40:00	2024-10-04	66	5
104	13:10:00	16:40:00	2024-10-11	66	5
105	13:10:00	16:40:00	2024-10-18	66	5
106	13:10:00	16:40:00	2024-10-25	66	5
107	13:10:00	16:40:00	2024-11-01	66	5
108	13:10:00	16:40:00	2024-11-08	66	5
109	13:10:00	16:40:00	2024-11-15	66	5
110	13:10:00	16:40:00	2024-11-22	66	5
111	13:10:00	16:40:00	2024-11-29	66	5
112	13:10:00	16:40:00	2024-12-06	66	5
113	13:10:00	16:40:00	2024-08-09	66	6
114	13:10:00	16:40:00	2024-08-16	66	6
115	13:10:00	16:40:00	2024-08-23	66	6
116	13:10:00	16:40:00	2024-08-30	66	6
117	13:10:00	16:40:00	2024-09-06	66	6
118	13:10:00	16:40:00	2024-09-13	66	6
119	13:10:00	16:40:00	2024-09-20	66	6
120	13:10:00	16:40:00	2024-09-27	66	6
121	13:10:00	16:40:00	2024-10-04	66	6
122	13:10:00	16:40:00	2024-10-11	66	6
123	13:10:00	16:40:00	2024-10-18	66	6
124	13:10:00	16:40:00	2024-10-25	66	6
125	13:10:00	16:40:00	2024-11-01	66	6
126	13:10:00	16:40:00	2024-11-08	66	6
127	13:10:00	16:40:00	2024-11-15	66	6
128	13:10:00	16:40:00	2024-11-22	66	6
129	13:10:00	16:40:00	2024-11-29	66	6
130	13:10:00	16:40:00	2024-12-06	66	6
131	13:10:00	14:50:00	2024-08-05	65	7
132	13:10:00	14:50:00	2024-08-12	65	7
133	13:10:00	14:50:00	2024-08-19	65	7
134	13:10:00	14:50:00	2024-08-26	65	7
135	13:10:00	14:50:00	2024-09-02	65	7
136	13:10:00	14:50:00	2024-09-09	65	7
137	13:10:00	14:50:00	2024-09-16	65	7
138	13:10:00	14:50:00	2024-09-23	65	7
139	13:10:00	14:50:00	2024-09-30	65	7
140	13:10:00	14:50:00	2024-10-07	65	7
141	13:10:00	14:50:00	2024-10-14	65	7
142	13:10:00	14:50:00	2024-10-21	65	7
143	13:10:00	14:50:00	2024-10-28	65	7
144	13:10:00	14:50:00	2024-11-04	65	7
145	13:10:00	14:50:00	2024-11-11	65	7
146	13:10:00	14:50:00	2024-11-18	65	7
147	13:10:00	14:50:00	2024-11-25	65	7
148	13:10:00	14:50:00	2024-12-02	65	7
149	13:10:00	14:50:00	2024-12-09	65	7
150	13:10:00	14:50:00	2024-08-07	35	8
151	13:10:00	14:50:00	2024-08-14	35	8
152	13:10:00	14:50:00	2024-08-21	35	8
153	13:10:00	14:50:00	2024-08-28	35	8
154	13:10:00	14:50:00	2024-09-04	35	8
155	13:10:00	14:50:00	2024-09-11	35	8
156	13:10:00	14:50:00	2024-09-18	35	8
157	13:10:00	14:50:00	2024-09-25	35	8
158	13:10:00	14:50:00	2024-10-02	35	8
159	13:10:00	14:50:00	2024-10-09	35	8
160	13:10:00	14:50:00	2024-10-16	35	8
161	13:10:00	14:50:00	2024-10-23	35	8
162	13:10:00	14:50:00	2024-10-30	35	8
163	13:10:00	14:50:00	2024-11-06	35	8
164	13:10:00	14:50:00	2024-11-13	35	8
165	13:10:00	14:50:00	2024-11-20	35	8
166	13:10:00	14:50:00	2024-11-27	35	8
167	13:10:00	14:50:00	2024-12-04	35	8
168	13:10:00	14:50:00	2024-12-11	35	8
169	09:20:00	11:00:00	2024-08-08	38	9
170	09:20:00	11:00:00	2024-08-15	38	9
171	09:20:00	11:00:00	2024-08-22	38	9
172	09:20:00	11:00:00	2024-08-29	38	9
173	09:20:00	11:00:00	2024-09-05	38	9
174	09:20:00	11:00:00	2024-09-12	38	9
175	09:20:00	11:00:00	2024-09-19	38	9
176	09:20:00	11:00:00	2024-09-26	38	9
177	09:20:00	11:00:00	2024-10-03	38	9
178	09:20:00	11:00:00	2024-10-10	38	9
179	09:20:00	11:00:00	2024-10-17	38	9
180	09:20:00	11:00:00	2024-10-24	38	9
181	09:20:00	11:00:00	2024-10-31	38	9
182	09:20:00	11:00:00	2024-11-07	38	9
183	09:20:00	11:00:00	2024-11-14	38	9
184	09:20:00	11:00:00	2024-11-21	38	9
185	09:20:00	11:00:00	2024-11-28	38	9
186	09:20:00	11:00:00	2024-12-05	38	9
187	09:20:00	11:00:00	2024-12-12	38	9
203	13:10:00	16:40:00	2024-05-08	67	11
204	13:10:00	16:40:00	2024-05-15	67	11
205	13:10:00	16:40:00	2024-05-22	67	11
206	13:10:00	16:40:00	2024-05-29	67	11
207	13:10:00	16:40:00	2024-06-05	67	11
208	13:10:00	16:40:00	2024-06-12	67	11
209	13:10:00	16:40:00	2024-06-19	67	11
210	13:10:00	16:40:00	2024-06-26	67	11
211	13:10:00	16:40:00	2024-07-03	67	11
212	13:10:00	16:40:00	2024-07-10	67	11
213	13:10:00	16:40:00	2024-07-17	67	11
214	13:10:00	16:40:00	2024-07-24	67	11
215	13:10:00	16:40:00	2024-07-31	67	11
216	13:10:00	16:40:00	2024-08-07	67	11
217	13:10:00	16:40:00	2024-08-14	67	11
218	13:10:00	16:40:00	2024-05-10	67	12
219	13:10:00	16:40:00	2024-05-17	67	12
220	13:10:00	16:40:00	2024-05-24	67	12
221	13:10:00	16:40:00	2024-05-31	67	12
222	13:10:00	16:40:00	2024-06-07	67	12
223	13:10:00	16:40:00	2024-06-14	67	12
224	13:10:00	16:40:00	2024-06-21	67	12
225	13:10:00	16:40:00	2024-06-28	67	12
226	13:10:00	16:40:00	2024-07-05	67	12
227	13:10:00	16:40:00	2024-07-12	67	12
228	13:10:00	16:40:00	2024-07-19	67	12
229	13:10:00	16:40:00	2024-07-26	67	12
230	13:10:00	16:40:00	2024-08-02	67	12
231	13:10:00	16:40:00	2024-08-09	67	12
232	13:10:00	16:40:00	2024-08-16	67	12
233	13:10:00	16:40:00	2024-05-10	67	13
234	13:10:00	16:40:00	2024-05-17	67	13
235	13:10:00	16:40:00	2024-05-24	67	13
236	13:10:00	16:40:00	2024-05-31	67	13
237	13:10:00	16:40:00	2024-06-07	67	13
238	13:10:00	16:40:00	2024-06-14	67	13
239	13:10:00	16:40:00	2024-06-21	67	13
240	13:10:00	16:40:00	2024-06-28	67	13
241	13:10:00	16:40:00	2024-07-05	67	13
242	13:10:00	16:40:00	2024-07-12	67	13
243	13:10:00	16:40:00	2024-07-19	67	13
244	13:10:00	16:40:00	2024-07-26	67	13
245	13:10:00	16:40:00	2024-08-02	67	13
246	13:10:00	16:40:00	2024-08-09	67	13
247	13:10:00	16:40:00	2024-08-16	67	13
263	08:20:00	11:00:00	2024-08-09	27	15
264	08:20:00	11:00:00	2024-08-16	27	15
265	08:20:00	11:00:00	2024-08-23	27	15
266	08:20:00	11:00:00	2024-08-30	27	15
267	08:20:00	11:00:00	2024-09-06	27	15
268	08:20:00	11:00:00	2024-09-13	27	15
269	08:20:00	11:00:00	2024-09-20	27	15
270	08:20:00	11:00:00	2024-09-27	27	15
271	08:20:00	11:00:00	2024-10-04	27	15
272	08:20:00	11:00:00	2024-10-11	27	15
273	08:20:00	11:00:00	2024-10-18	27	15
274	08:20:00	11:00:00	2024-10-25	27	15
275	08:20:00	11:00:00	2024-11-01	27	15
276	08:20:00	11:00:00	2024-11-08	27	15
277	08:20:00	11:00:00	2024-11-15	27	15
278	08:20:00	11:00:00	2024-11-22	27	15
279	08:20:00	11:00:00	2024-11-29	27	15
280	08:20:00	11:00:00	2024-12-06	27	15
281	07:30:00	11:00:00	2024-08-08	66	16
282	07:30:00	11:00:00	2024-08-15	66	16
283	07:30:00	11:00:00	2024-08-22	66	16
284	07:30:00	11:00:00	2024-08-29	66	16
285	07:30:00	11:00:00	2024-09-05	66	16
286	07:30:00	11:00:00	2024-09-12	66	16
287	07:30:00	11:00:00	2024-09-19	66	16
288	07:30:00	11:00:00	2024-09-26	66	16
289	07:30:00	11:00:00	2024-10-03	66	16
290	07:30:00	11:00:00	2024-10-10	66	16
291	07:30:00	11:00:00	2024-10-17	66	16
292	07:30:00	11:00:00	2024-10-24	66	16
293	07:30:00	11:00:00	2024-10-31	66	16
294	07:30:00	11:00:00	2024-11-07	66	16
295	07:30:00	11:00:00	2024-11-14	66	16
296	07:30:00	11:00:00	2024-11-21	66	16
297	07:30:00	11:00:00	2024-11-28	66	16
298	07:30:00	11:00:00	2024-12-05	66	16
299	07:30:00	11:00:00	2024-12-12	66	16
300	07:30:00	11:00:00	2024-08-08	66	17
301	07:30:00	11:00:00	2024-08-15	66	17
302	07:30:00	11:00:00	2024-08-22	66	17
303	07:30:00	11:00:00	2024-08-29	66	17
304	07:30:00	11:00:00	2024-09-05	66	17
305	07:30:00	11:00:00	2024-09-12	66	17
306	07:30:00	11:00:00	2024-09-19	66	17
307	07:30:00	11:00:00	2024-09-26	66	17
308	07:30:00	11:00:00	2024-10-03	66	17
309	07:30:00	11:00:00	2024-10-10	66	17
310	07:30:00	11:00:00	2024-10-17	66	17
311	07:30:00	11:00:00	2024-10-24	66	17
312	07:30:00	11:00:00	2024-10-31	66	17
313	07:30:00	11:00:00	2024-11-07	66	17
314	07:30:00	11:00:00	2024-11-14	66	17
315	07:30:00	11:00:00	2024-11-21	66	17
316	07:30:00	11:00:00	2024-11-28	66	17
317	07:30:00	11:00:00	2024-12-05	66	17
318	07:30:00	11:00:00	2024-12-12	66	17
319	14:00:00	17:30:00	2024-08-08	66	18
320	14:00:00	17:30:00	2024-08-15	66	18
321	14:00:00	17:30:00	2024-08-22	66	18
322	14:00:00	17:30:00	2024-08-29	66	18
323	14:00:00	17:30:00	2024-09-05	66	18
324	14:00:00	17:30:00	2024-09-12	66	18
325	14:00:00	17:30:00	2024-09-19	66	18
326	14:00:00	17:30:00	2024-09-26	66	18
327	14:00:00	17:30:00	2024-10-03	66	18
328	14:00:00	17:30:00	2024-10-10	66	18
329	14:00:00	17:30:00	2024-10-17	66	18
330	14:00:00	17:30:00	2024-10-24	66	18
331	14:00:00	17:30:00	2024-10-31	66	18
332	14:00:00	17:30:00	2024-11-07	66	18
333	14:00:00	17:30:00	2024-11-14	66	18
334	14:00:00	17:30:00	2024-11-21	66	18
335	14:00:00	17:30:00	2024-11-28	66	18
336	14:00:00	17:30:00	2024-12-05	66	18
337	14:00:00	17:30:00	2024-12-12	66	18
338	14:00:00	17:30:00	2024-08-08	66	19
339	14:00:00	17:30:00	2024-08-15	66	19
340	14:00:00	17:30:00	2024-08-22	66	19
341	14:00:00	17:30:00	2024-08-29	66	19
342	14:00:00	17:30:00	2024-09-05	66	19
343	14:00:00	17:30:00	2024-09-12	66	19
344	14:00:00	17:30:00	2024-09-19	66	19
345	14:00:00	17:30:00	2024-09-26	66	19
346	14:00:00	17:30:00	2024-10-03	66	19
347	14:00:00	17:30:00	2024-10-10	66	19
348	14:00:00	17:30:00	2024-10-17	66	19
349	14:00:00	17:30:00	2024-10-24	66	19
350	14:00:00	17:30:00	2024-10-31	66	19
351	14:00:00	17:30:00	2024-11-07	66	19
352	14:00:00	17:30:00	2024-11-14	66	19
353	14:00:00	17:30:00	2024-11-21	66	19
354	14:00:00	17:30:00	2024-11-28	66	19
355	14:00:00	17:30:00	2024-12-05	66	19
356	14:00:00	17:30:00	2024-12-12	66	19
357	07:30:00	09:10:00	2024-08-07	38	20
358	07:30:00	09:10:00	2024-08-14	38	20
359	07:30:00	09:10:00	2024-08-21	38	20
360	07:30:00	09:10:00	2024-08-28	38	20
361	07:30:00	09:10:00	2024-09-04	38	20
362	07:30:00	09:10:00	2024-09-11	38	20
363	07:30:00	09:10:00	2024-09-18	38	20
364	07:30:00	09:10:00	2024-09-25	38	20
365	07:30:00	09:10:00	2024-10-02	38	20
366	07:30:00	09:10:00	2024-10-09	38	20
367	07:30:00	09:10:00	2024-10-16	38	20
368	07:30:00	09:10:00	2024-10-23	38	20
369	07:30:00	09:10:00	2024-10-30	38	20
370	07:30:00	09:10:00	2024-11-06	38	20
371	07:30:00	09:10:00	2024-11-13	38	20
372	07:30:00	09:10:00	2024-11-20	38	20
373	07:30:00	09:10:00	2024-11-27	38	20
374	07:30:00	09:10:00	2024-12-04	38	20
375	07:30:00	09:10:00	2024-12-11	38	20
376	15:00:00	16:40:00	2024-08-05	65	25
377	15:00:00	16:40:00	2024-08-12	65	25
378	15:00:00	16:40:00	2024-08-19	65	25
379	15:00:00	16:40:00	2024-08-26	65	25
380	15:00:00	16:40:00	2024-09-02	65	25
381	15:00:00	16:40:00	2024-09-09	65	25
382	15:00:00	16:40:00	2024-09-16	65	25
383	15:00:00	16:40:00	2024-09-23	65	25
384	15:00:00	16:40:00	2024-09-30	65	25
385	15:00:00	16:40:00	2024-10-07	65	25
386	15:00:00	16:40:00	2024-10-14	65	25
387	15:00:00	16:40:00	2024-10-21	65	25
388	15:00:00	16:40:00	2024-10-28	65	25
389	15:00:00	16:40:00	2024-11-04	65	25
390	15:00:00	16:40:00	2024-11-11	65	25
391	15:00:00	16:40:00	2024-11-18	65	25
392	15:00:00	16:40:00	2024-11-25	65	25
393	15:00:00	16:40:00	2024-12-02	65	25
394	15:00:00	16:40:00	2024-12-09	65	25
395	07:30:00	11:00:00	2024-08-07	66	21
396	07:30:00	11:00:00	2024-08-14	66	21
397	07:30:00	11:00:00	2024-08-21	66	21
398	07:30:00	11:00:00	2024-08-28	66	21
399	07:30:00	11:00:00	2024-09-04	66	21
400	07:30:00	11:00:00	2024-09-11	66	21
401	07:30:00	11:00:00	2024-09-18	66	21
402	07:30:00	11:00:00	2024-09-25	66	21
403	07:30:00	11:00:00	2024-10-02	66	21
404	07:30:00	11:00:00	2024-10-09	66	21
405	07:30:00	11:00:00	2024-10-16	66	21
406	07:30:00	11:00:00	2024-10-23	66	21
407	07:30:00	11:00:00	2024-10-30	66	21
408	07:30:00	11:00:00	2024-11-06	66	21
409	07:30:00	11:00:00	2024-11-13	66	21
410	07:30:00	11:00:00	2024-11-20	66	21
411	07:30:00	11:00:00	2024-11-27	66	21
412	07:30:00	11:00:00	2024-12-04	66	21
413	07:30:00	11:00:00	2024-12-11	66	21
414	07:30:00	11:00:00	2024-08-07	66	22
415	07:30:00	11:00:00	2024-08-14	66	22
416	07:30:00	11:00:00	2024-08-21	66	22
417	07:30:00	11:00:00	2024-08-28	66	22
418	07:30:00	11:00:00	2024-09-04	66	22
419	07:30:00	11:00:00	2024-09-11	66	22
420	07:30:00	11:00:00	2024-09-18	66	22
421	07:30:00	11:00:00	2024-09-25	66	22
422	07:30:00	11:00:00	2024-10-02	66	22
423	07:30:00	11:00:00	2024-10-09	66	22
424	07:30:00	11:00:00	2024-10-16	66	22
425	07:30:00	11:00:00	2024-10-23	66	22
426	07:30:00	11:00:00	2024-10-30	66	22
427	07:30:00	11:00:00	2024-11-06	66	22
428	07:30:00	11:00:00	2024-11-13	66	22
429	07:30:00	11:00:00	2024-11-20	66	22
430	07:30:00	11:00:00	2024-11-27	66	22
431	07:30:00	11:00:00	2024-12-04	66	22
432	07:30:00	11:00:00	2024-12-11	66	22
433	07:30:00	11:00:00	2024-08-09	66	23
434	07:30:00	11:00:00	2024-08-16	66	23
435	07:30:00	11:00:00	2024-08-23	66	23
436	07:30:00	11:00:00	2024-08-30	66	23
437	07:30:00	11:00:00	2024-09-06	66	23
438	07:30:00	11:00:00	2024-09-13	66	23
439	07:30:00	11:00:00	2024-09-20	66	23
440	07:30:00	11:00:00	2024-09-27	66	23
441	07:30:00	11:00:00	2024-10-04	66	23
442	07:30:00	11:00:00	2024-10-11	66	23
443	07:30:00	11:00:00	2024-10-18	66	23
444	07:30:00	11:00:00	2024-10-25	66	23
445	07:30:00	11:00:00	2024-11-01	66	23
446	07:30:00	11:00:00	2024-11-08	66	23
447	07:30:00	11:00:00	2024-11-15	66	23
448	07:30:00	11:00:00	2024-11-22	66	23
449	07:30:00	11:00:00	2024-11-29	66	23
450	07:30:00	11:00:00	2024-12-06	66	23
451	07:30:00	11:00:00	2024-08-09	66	24
452	07:30:00	11:00:00	2024-08-16	66	24
453	07:30:00	11:00:00	2024-08-23	66	24
454	07:30:00	11:00:00	2024-08-30	66	24
455	07:30:00	11:00:00	2024-09-06	66	24
456	07:30:00	11:00:00	2024-09-13	66	24
457	07:30:00	11:00:00	2024-09-20	66	24
458	07:30:00	11:00:00	2024-09-27	66	24
459	07:30:00	11:00:00	2024-10-04	66	24
460	07:30:00	11:00:00	2024-10-11	66	24
461	07:30:00	11:00:00	2024-10-18	66	24
462	07:30:00	11:00:00	2024-10-25	66	24
463	07:30:00	11:00:00	2024-11-01	66	24
464	07:30:00	11:00:00	2024-11-08	66	24
465	07:30:00	11:00:00	2024-11-15	66	24
466	07:30:00	11:00:00	2024-11-22	66	24
467	07:30:00	11:00:00	2024-11-29	66	24
468	07:30:00	11:00:00	2024-12-06	66	24
469	07:30:00	11:00:00	2024-08-08	27	26
470	07:30:00	11:00:00	2024-08-15	27	26
471	07:30:00	11:00:00	2024-08-22	27	26
472	07:30:00	11:00:00	2024-08-29	27	26
473	07:30:00	11:00:00	2024-09-05	27	26
474	07:30:00	11:00:00	2024-09-12	27	26
475	07:30:00	11:00:00	2024-09-19	27	26
476	07:30:00	11:00:00	2024-09-26	27	26
477	07:30:00	11:00:00	2024-10-03	27	26
478	07:30:00	11:00:00	2024-10-10	27	26
479	07:30:00	11:00:00	2024-10-17	27	26
480	07:30:00	11:00:00	2024-10-24	27	26
481	07:30:00	11:00:00	2024-10-31	27	26
482	07:30:00	11:00:00	2024-11-07	27	26
483	07:30:00	11:00:00	2024-11-14	27	26
484	07:30:00	11:00:00	2024-11-21	27	26
485	07:30:00	11:00:00	2024-11-28	27	26
486	07:30:00	11:00:00	2024-12-05	27	26
487	07:30:00	11:00:00	2024-12-12	27	26
488	07:30:00	11:00:00	2024-08-08	27	27
489	07:30:00	11:00:00	2024-08-15	27	27
490	07:30:00	11:00:00	2024-08-22	27	27
491	07:30:00	11:00:00	2024-08-29	27	27
492	07:30:00	11:00:00	2024-09-05	27	27
493	07:30:00	11:00:00	2024-09-12	27	27
494	07:30:00	11:00:00	2024-09-19	27	27
495	07:30:00	11:00:00	2024-09-26	27	27
496	07:30:00	11:00:00	2024-10-03	27	27
497	07:30:00	11:00:00	2024-10-10	27	27
498	07:30:00	11:00:00	2024-10-17	27	27
499	07:30:00	11:00:00	2024-10-24	27	27
500	07:30:00	11:00:00	2024-10-31	27	27
501	07:30:00	11:00:00	2024-11-07	27	27
502	07:30:00	11:00:00	2024-11-14	27	27
503	07:30:00	11:00:00	2024-11-21	27	27
504	07:30:00	11:00:00	2024-11-28	27	27
505	07:30:00	11:00:00	2024-12-05	27	27
506	07:30:00	11:00:00	2024-12-12	27	27
507	13:10:00	16:40:00	2024-08-09	27	28
508	13:10:00	16:40:00	2024-08-16	27	28
509	13:10:00	16:40:00	2024-08-23	27	28
510	13:10:00	16:40:00	2024-08-30	27	28
511	13:10:00	16:40:00	2024-09-06	27	28
512	13:10:00	16:40:00	2024-09-13	27	28
513	13:10:00	16:40:00	2024-09-20	27	28
514	13:10:00	16:40:00	2024-09-27	27	28
515	13:10:00	16:40:00	2024-10-04	27	28
516	13:10:00	16:40:00	2024-10-11	27	28
517	13:10:00	16:40:00	2024-10-18	27	28
518	13:10:00	16:40:00	2024-10-25	27	28
519	13:10:00	16:40:00	2024-11-01	27	28
520	13:10:00	16:40:00	2024-11-08	27	28
521	13:10:00	16:40:00	2024-11-15	27	28
522	13:10:00	16:40:00	2024-11-22	27	28
523	13:10:00	16:40:00	2024-11-29	27	28
524	13:10:00	16:40:00	2024-12-06	27	28
525	15:00:00	16:40:00	2024-08-05	35	33
526	15:00:00	16:40:00	2024-08-12	35	33
527	15:00:00	16:40:00	2024-08-19	35	33
528	15:00:00	16:40:00	2024-08-26	35	33
529	15:00:00	16:40:00	2024-09-02	35	33
530	15:00:00	16:40:00	2024-09-09	35	33
531	15:00:00	16:40:00	2024-09-16	35	33
532	15:00:00	16:40:00	2024-09-23	35	33
533	15:00:00	16:40:00	2024-09-30	35	33
534	15:00:00	16:40:00	2024-10-07	35	33
535	15:00:00	16:40:00	2024-10-14	35	33
536	15:00:00	16:40:00	2024-10-21	35	33
537	15:00:00	16:40:00	2024-10-28	35	33
538	15:00:00	16:40:00	2024-11-04	35	33
539	15:00:00	16:40:00	2024-11-11	35	33
540	15:00:00	16:40:00	2024-11-18	35	33
541	15:00:00	16:40:00	2024-11-25	35	33
542	15:00:00	16:40:00	2024-12-02	35	33
543	15:00:00	16:40:00	2024-12-09	35	33
544	15:00:00	16:40:00	2024-08-07	67	275
545	15:00:00	16:40:00	2024-08-14	67	275
546	15:00:00	16:40:00	2024-08-21	67	275
547	15:00:00	16:40:00	2024-08-28	67	275
548	15:00:00	16:40:00	2024-09-04	67	275
549	15:00:00	16:40:00	2024-09-11	67	275
550	15:00:00	16:40:00	2024-09-18	67	275
551	15:00:00	16:40:00	2024-09-25	67	275
552	15:00:00	16:40:00	2024-10-02	67	275
553	15:00:00	16:40:00	2024-10-09	67	275
554	15:00:00	16:40:00	2024-10-16	67	275
555	15:00:00	16:40:00	2024-10-23	67	275
556	15:00:00	16:40:00	2024-10-30	67	275
557	15:00:00	16:40:00	2024-11-06	67	275
558	15:00:00	16:40:00	2024-11-13	67	275
559	15:00:00	16:40:00	2024-11-20	67	275
560	15:00:00	16:40:00	2024-11-27	67	275
561	15:00:00	16:40:00	2024-12-04	67	275
562	15:00:00	16:40:00	2024-12-11	67	275
563	13:10:00	14:50:00	2024-08-07	27	34
564	13:10:00	14:50:00	2024-08-14	27	34
565	13:10:00	14:50:00	2024-08-21	27	34
566	13:10:00	14:50:00	2024-08-28	27	34
567	13:10:00	14:50:00	2024-09-04	27	34
568	13:10:00	14:50:00	2024-09-11	27	34
569	13:10:00	14:50:00	2024-09-18	27	34
570	13:10:00	14:50:00	2024-09-25	27	34
571	13:10:00	14:50:00	2024-10-02	27	34
572	13:10:00	14:50:00	2024-10-09	27	34
573	13:10:00	14:50:00	2024-10-16	27	34
574	13:10:00	14:50:00	2024-10-23	27	34
575	13:10:00	14:50:00	2024-10-30	27	34
576	13:10:00	14:50:00	2024-11-06	27	34
577	13:10:00	14:50:00	2024-11-13	27	34
578	13:10:00	14:50:00	2024-11-20	27	34
579	13:10:00	14:50:00	2024-11-27	27	34
580	13:10:00	14:50:00	2024-12-04	27	34
581	13:10:00	14:50:00	2024-12-11	27	34
582	15:00:00	16:40:00	2024-08-08	27	35
583	15:00:00	16:40:00	2024-08-15	27	35
584	15:00:00	16:40:00	2024-08-22	27	35
585	15:00:00	16:40:00	2024-08-29	27	35
586	15:00:00	16:40:00	2024-09-05	27	35
587	15:00:00	16:40:00	2024-09-12	27	35
588	15:00:00	16:40:00	2024-09-19	27	35
589	15:00:00	16:40:00	2024-09-26	27	35
590	15:00:00	16:40:00	2024-10-03	27	35
591	15:00:00	16:40:00	2024-10-10	27	35
592	15:00:00	16:40:00	2024-10-17	27	35
593	15:00:00	16:40:00	2024-10-24	27	35
594	15:00:00	16:40:00	2024-10-31	27	35
595	15:00:00	16:40:00	2024-11-07	27	35
596	15:00:00	16:40:00	2024-11-14	27	35
597	15:00:00	16:40:00	2024-11-21	27	35
598	15:00:00	16:40:00	2024-11-28	27	35
599	15:00:00	16:40:00	2024-12-05	27	35
600	15:00:00	16:40:00	2024-12-12	27	35
601	07:30:00	11:00:00	2024-08-07	67	36
602	07:30:00	11:00:00	2024-08-14	67	36
603	07:30:00	11:00:00	2024-08-21	67	36
604	07:30:00	11:00:00	2024-08-28	67	36
605	07:30:00	11:00:00	2024-09-04	67	36
606	07:30:00	11:00:00	2024-09-11	67	36
607	07:30:00	11:00:00	2024-09-18	67	36
608	07:30:00	11:00:00	2024-09-25	67	36
609	07:30:00	11:00:00	2024-10-02	67	36
610	07:30:00	11:00:00	2024-10-09	67	36
611	07:30:00	11:00:00	2024-10-16	67	36
612	07:30:00	11:00:00	2024-10-23	67	36
613	07:30:00	11:00:00	2024-10-30	67	36
614	07:30:00	11:00:00	2024-11-06	67	36
615	07:30:00	11:00:00	2024-11-13	67	36
616	07:30:00	11:00:00	2024-11-20	67	36
617	07:30:00	11:00:00	2024-11-27	67	36
618	07:30:00	11:00:00	2024-12-04	67	36
619	07:30:00	11:00:00	2024-12-11	67	36
620	07:30:00	11:00:00	2024-08-07	67	37
621	07:30:00	11:00:00	2024-08-14	67	37
622	07:30:00	11:00:00	2024-08-21	67	37
623	07:30:00	11:00:00	2024-08-28	67	37
624	07:30:00	11:00:00	2024-09-04	67	37
625	07:30:00	11:00:00	2024-09-11	67	37
626	07:30:00	11:00:00	2024-09-18	67	37
627	07:30:00	11:00:00	2024-09-25	67	37
628	07:30:00	11:00:00	2024-10-02	67	37
629	07:30:00	11:00:00	2024-10-09	67	37
630	07:30:00	11:00:00	2024-10-16	67	37
631	07:30:00	11:00:00	2024-10-23	67	37
632	07:30:00	11:00:00	2024-10-30	67	37
633	07:30:00	11:00:00	2024-11-06	67	37
634	07:30:00	11:00:00	2024-11-13	67	37
635	07:30:00	11:00:00	2024-11-20	67	37
636	07:30:00	11:00:00	2024-11-27	67	37
637	07:30:00	11:00:00	2024-12-04	67	37
638	07:30:00	11:00:00	2024-12-11	67	37
639	16:50:00	18:30:00	2024-08-07	67	38
640	16:50:00	18:30:00	2024-08-14	67	38
641	16:50:00	18:30:00	2024-08-21	67	38
642	16:50:00	18:30:00	2024-08-28	67	38
643	16:50:00	18:30:00	2024-09-04	67	38
644	16:50:00	18:30:00	2024-09-11	67	38
645	16:50:00	18:30:00	2024-09-18	67	38
646	16:50:00	18:30:00	2024-09-25	67	38
647	16:50:00	18:30:00	2024-10-02	67	38
648	16:50:00	18:30:00	2024-10-09	67	38
649	16:50:00	18:30:00	2024-10-16	67	38
650	16:50:00	18:30:00	2024-10-23	67	38
651	16:50:00	18:30:00	2024-10-30	67	38
652	16:50:00	18:30:00	2024-11-06	67	38
653	16:50:00	18:30:00	2024-11-13	67	38
654	16:50:00	18:30:00	2024-11-20	67	38
655	16:50:00	18:30:00	2024-11-27	67	38
656	16:50:00	18:30:00	2024-12-04	67	38
657	16:50:00	18:30:00	2024-12-11	67	38
658	16:50:00	18:30:00	2024-08-05	27	41
659	16:50:00	18:30:00	2024-08-12	27	41
660	16:50:00	18:30:00	2024-08-19	27	41
661	16:50:00	18:30:00	2024-08-26	27	41
662	16:50:00	18:30:00	2024-09-02	27	41
663	16:50:00	18:30:00	2024-09-09	27	41
664	16:50:00	18:30:00	2024-09-16	27	41
665	16:50:00	18:30:00	2024-09-23	27	41
666	16:50:00	18:30:00	2024-09-30	27	41
667	16:50:00	18:30:00	2024-10-07	27	41
668	16:50:00	18:30:00	2024-10-14	27	41
669	16:50:00	18:30:00	2024-10-21	27	41
670	16:50:00	18:30:00	2024-10-28	27	41
671	16:50:00	18:30:00	2024-11-04	27	41
672	16:50:00	18:30:00	2024-11-11	27	41
673	16:50:00	18:30:00	2024-11-18	27	41
674	16:50:00	18:30:00	2024-11-25	27	41
675	16:50:00	18:30:00	2024-12-02	27	41
676	16:50:00	18:30:00	2024-12-09	27	41
696	13:10:00	14:50:00	2024-08-05	35	45
697	13:10:00	14:50:00	2024-08-12	35	45
698	13:10:00	14:50:00	2024-08-19	35	45
699	13:10:00	14:50:00	2024-08-26	35	45
700	13:10:00	14:50:00	2024-09-02	35	45
701	13:10:00	14:50:00	2024-09-09	35	45
702	13:10:00	14:50:00	2024-09-16	35	45
703	13:10:00	14:50:00	2024-09-23	35	45
704	13:10:00	14:50:00	2024-09-30	35	45
705	13:10:00	14:50:00	2024-10-07	35	45
706	13:10:00	14:50:00	2024-10-14	35	45
707	13:10:00	14:50:00	2024-10-21	35	45
708	13:10:00	14:50:00	2024-10-28	35	45
709	13:10:00	14:50:00	2024-11-04	35	45
710	13:10:00	14:50:00	2024-11-11	35	45
711	13:10:00	14:50:00	2024-11-18	35	45
712	13:10:00	14:50:00	2024-11-25	35	45
713	13:10:00	14:50:00	2024-12-02	35	45
714	13:10:00	14:50:00	2024-12-09	35	45
715	09:20:00	11:10:00	2024-08-10	68	46
716	09:20:00	11:10:00	2024-08-17	68	46
717	09:20:00	11:10:00	2024-08-24	68	46
718	09:20:00	11:10:00	2024-08-31	68	46
719	09:20:00	11:10:00	2024-09-07	68	46
720	09:20:00	11:10:00	2024-09-14	68	46
721	09:20:00	11:10:00	2024-09-21	68	46
722	09:20:00	11:10:00	2024-09-28	68	46
723	09:20:00	11:10:00	2024-10-05	68	46
724	09:20:00	11:10:00	2024-10-12	68	46
725	09:20:00	11:10:00	2024-10-19	68	46
726	09:20:00	11:10:00	2024-10-26	68	46
727	09:20:00	11:10:00	2024-11-02	68	46
728	09:20:00	11:10:00	2024-11-09	68	46
729	09:20:00	11:10:00	2024-11-16	68	46
730	09:20:00	11:10:00	2024-11-23	68	46
731	09:20:00	11:10:00	2024-11-30	68	46
732	09:20:00	11:10:00	2024-12-07	68	46
733	07:30:00	09:10:00	2024-08-10	68	47
734	07:30:00	09:10:00	2024-08-17	68	47
735	07:30:00	09:10:00	2024-08-24	68	47
736	07:30:00	09:10:00	2024-08-31	68	47
737	07:30:00	09:10:00	2024-09-07	68	47
738	07:30:00	09:10:00	2024-09-14	68	47
739	07:30:00	09:10:00	2024-09-21	68	47
740	07:30:00	09:10:00	2024-09-28	68	47
741	07:30:00	09:10:00	2024-10-05	68	47
742	07:30:00	09:10:00	2024-10-12	68	47
743	07:30:00	09:10:00	2024-10-19	68	47
744	07:30:00	09:10:00	2024-10-26	68	47
745	07:30:00	09:10:00	2024-11-02	68	47
746	07:30:00	09:10:00	2024-11-09	68	47
747	07:30:00	09:10:00	2024-11-16	68	47
748	07:30:00	09:10:00	2024-11-23	68	47
749	07:30:00	09:10:00	2024-11-30	68	47
750	07:30:00	09:10:00	2024-12-07	68	47
751	07:30:00	09:10:00	2024-08-10	68	48
752	07:30:00	09:10:00	2024-08-17	68	48
753	07:30:00	09:10:00	2024-08-24	68	48
754	07:30:00	09:10:00	2024-08-31	68	48
755	07:30:00	09:10:00	2024-09-07	68	48
756	07:30:00	09:10:00	2024-09-14	68	48
757	07:30:00	09:10:00	2024-09-21	68	48
758	07:30:00	09:10:00	2024-09-28	68	48
759	07:30:00	09:10:00	2024-10-05	68	48
760	07:30:00	09:10:00	2024-10-12	68	48
761	07:30:00	09:10:00	2024-10-19	68	48
762	07:30:00	09:10:00	2024-10-26	68	48
763	07:30:00	09:10:00	2024-11-02	68	48
764	07:30:00	09:10:00	2024-11-09	68	48
765	07:30:00	09:10:00	2024-11-16	68	48
766	07:30:00	09:10:00	2024-11-23	68	48
767	07:30:00	09:10:00	2024-11-30	68	48
768	07:30:00	09:10:00	2024-12-07	68	48
769	07:30:00	09:10:00	2024-08-10	68	49
770	07:30:00	09:10:00	2024-08-17	68	49
771	07:30:00	09:10:00	2024-08-24	68	49
772	07:30:00	09:10:00	2024-08-31	68	49
773	07:30:00	09:10:00	2024-09-07	68	49
774	07:30:00	09:10:00	2024-09-14	68	49
775	07:30:00	09:10:00	2024-09-21	68	49
776	07:30:00	09:10:00	2024-09-28	68	49
777	07:30:00	09:10:00	2024-10-05	68	49
778	07:30:00	09:10:00	2024-10-12	68	49
779	07:30:00	09:10:00	2024-10-19	68	49
780	07:30:00	09:10:00	2024-10-26	68	49
781	07:30:00	09:10:00	2024-11-02	68	49
782	07:30:00	09:10:00	2024-11-09	68	49
783	07:30:00	09:10:00	2024-11-16	68	49
784	07:30:00	09:10:00	2024-11-23	68	49
785	07:30:00	09:10:00	2024-11-30	68	49
786	07:30:00	09:10:00	2024-12-07	68	49
787	07:30:00	09:10:00	2024-08-10	68	50
788	07:30:00	09:10:00	2024-08-17	68	50
789	07:30:00	09:10:00	2024-08-24	68	50
790	07:30:00	09:10:00	2024-08-31	68	50
791	07:30:00	09:10:00	2024-09-07	68	50
792	07:30:00	09:10:00	2024-09-14	68	50
793	07:30:00	09:10:00	2024-09-21	68	50
794	07:30:00	09:10:00	2024-09-28	68	50
795	07:30:00	09:10:00	2024-10-05	68	50
796	07:30:00	09:10:00	2024-10-12	68	50
797	07:30:00	09:10:00	2024-10-19	68	50
798	07:30:00	09:10:00	2024-10-26	68	50
799	07:30:00	09:10:00	2024-11-02	68	50
800	07:30:00	09:10:00	2024-11-09	68	50
801	07:30:00	09:10:00	2024-11-16	68	50
802	07:30:00	09:10:00	2024-11-23	68	50
803	07:30:00	09:10:00	2024-11-30	68	50
804	07:30:00	09:10:00	2024-12-07	68	50
805	07:30:00	09:10:00	2024-08-10	68	51
806	07:30:00	09:10:00	2024-08-17	68	51
807	07:30:00	09:10:00	2024-08-24	68	51
808	07:30:00	09:10:00	2024-08-31	68	51
809	07:30:00	09:10:00	2024-09-07	68	51
810	07:30:00	09:10:00	2024-09-14	68	51
811	07:30:00	09:10:00	2024-09-21	68	51
812	07:30:00	09:10:00	2024-09-28	68	51
813	07:30:00	09:10:00	2024-10-05	68	51
814	07:30:00	09:10:00	2024-10-12	68	51
815	07:30:00	09:10:00	2024-10-19	68	51
816	07:30:00	09:10:00	2024-10-26	68	51
817	07:30:00	09:10:00	2024-11-02	68	51
818	07:30:00	09:10:00	2024-11-09	68	51
819	07:30:00	09:10:00	2024-11-16	68	51
820	07:30:00	09:10:00	2024-11-23	68	51
821	07:30:00	09:10:00	2024-11-30	68	51
822	07:30:00	09:10:00	2024-12-07	68	51
823	13:10:00	14:50:00	2024-08-08	32	263
824	13:10:00	14:50:00	2024-08-15	32	263
825	13:10:00	14:50:00	2024-08-22	32	263
826	13:10:00	14:50:00	2024-08-29	32	263
827	13:10:00	14:50:00	2024-09-05	32	263
828	13:10:00	14:50:00	2024-09-12	32	263
829	13:10:00	14:50:00	2024-09-19	32	263
830	13:10:00	14:50:00	2024-09-26	32	263
831	13:10:00	14:50:00	2024-10-03	32	263
832	13:10:00	14:50:00	2024-10-10	32	263
833	13:10:00	14:50:00	2024-10-17	32	263
834	13:10:00	14:50:00	2024-10-24	32	263
835	13:10:00	14:50:00	2024-10-31	32	263
836	13:10:00	14:50:00	2024-11-07	32	263
837	13:10:00	14:50:00	2024-11-14	32	263
838	13:10:00	14:50:00	2024-11-21	32	263
839	13:10:00	14:50:00	2024-11-28	32	263
840	13:10:00	14:50:00	2024-12-05	32	263
841	13:10:00	14:50:00	2024-12-12	32	263
842	07:30:00	09:10:00	2024-08-07	32	264
843	07:30:00	09:10:00	2024-08-14	32	264
844	07:30:00	09:10:00	2024-08-21	32	264
845	07:30:00	09:10:00	2024-08-28	32	264
846	07:30:00	09:10:00	2024-09-04	32	264
847	07:30:00	09:10:00	2024-09-11	32	264
848	07:30:00	09:10:00	2024-09-18	32	264
849	07:30:00	09:10:00	2024-09-25	32	264
850	07:30:00	09:10:00	2024-10-02	32	264
851	07:30:00	09:10:00	2024-10-09	32	264
852	07:30:00	09:10:00	2024-10-16	32	264
853	07:30:00	09:10:00	2024-10-23	32	264
854	07:30:00	09:10:00	2024-10-30	32	264
855	07:30:00	09:10:00	2024-11-06	32	264
856	07:30:00	09:10:00	2024-11-13	32	264
857	07:30:00	09:10:00	2024-11-20	32	264
858	07:30:00	09:10:00	2024-11-27	32	264
859	07:30:00	09:10:00	2024-12-04	32	264
860	07:30:00	09:10:00	2024-12-11	32	264
4374	07:30:00	11:00:00	2024-08-06	27	52
4375	07:30:00	11:00:00	2024-08-13	27	52
4376	07:30:00	11:00:00	2024-08-20	27	52
4377	07:30:00	11:00:00	2024-08-27	27	52
4378	07:30:00	11:00:00	2024-09-03	27	52
4379	07:30:00	11:00:00	2024-09-10	27	52
4380	07:30:00	11:00:00	2024-09-17	27	52
4381	07:30:00	11:00:00	2024-09-24	27	52
4382	07:30:00	11:00:00	2024-10-01	27	52
4383	07:30:00	11:00:00	2024-10-08	27	52
4384	07:30:00	11:00:00	2024-10-15	27	52
4385	07:30:00	11:00:00	2024-10-22	27	52
4386	07:30:00	11:00:00	2024-10-29	27	52
4387	07:30:00	11:00:00	2024-11-05	27	52
4388	07:30:00	11:00:00	2024-11-12	27	52
4389	07:30:00	11:00:00	2024-11-19	27	52
4390	07:30:00	11:00:00	2024-11-26	27	52
4391	07:30:00	11:00:00	2024-12-03	27	52
4392	07:30:00	11:00:00	2024-12-10	27	52
4449	09:20:00	11:00:00	2024-08-05	30	56
4450	09:20:00	11:00:00	2024-08-12	30	56
4451	09:20:00	11:00:00	2024-08-19	30	56
4452	09:20:00	11:00:00	2024-08-26	30	56
4453	09:20:00	11:00:00	2024-09-02	30	56
4454	09:20:00	11:00:00	2024-09-09	30	56
4455	09:20:00	11:00:00	2024-09-16	30	56
4456	09:20:00	11:00:00	2024-09-23	30	56
4457	09:20:00	11:00:00	2024-09-30	30	56
4458	09:20:00	11:00:00	2024-10-07	30	56
4459	09:20:00	11:00:00	2024-10-14	30	56
4460	09:20:00	11:00:00	2024-10-21	30	56
4461	09:20:00	11:00:00	2024-10-28	30	56
4462	09:20:00	11:00:00	2024-11-04	30	56
4463	09:20:00	11:00:00	2024-11-11	30	56
4464	09:20:00	11:00:00	2024-11-18	30	56
4465	09:20:00	11:00:00	2024-11-25	30	56
4466	09:20:00	11:00:00	2024-12-02	30	56
4467	09:20:00	11:00:00	2024-12-09	30	56
4468	09:20:00	11:00:00	2024-08-08	32	57
4469	09:20:00	11:00:00	2024-08-15	32	57
4470	09:20:00	11:00:00	2024-08-22	32	57
4471	09:20:00	11:00:00	2024-08-29	32	57
4472	09:20:00	11:00:00	2024-09-05	32	57
4473	09:20:00	11:00:00	2024-09-12	32	57
4474	09:20:00	11:00:00	2024-09-19	32	57
4475	09:20:00	11:00:00	2024-09-26	32	57
4476	09:20:00	11:00:00	2024-10-03	32	57
4477	09:20:00	11:00:00	2024-10-10	32	57
4478	09:20:00	11:00:00	2024-10-17	32	57
4479	09:20:00	11:00:00	2024-10-24	32	57
4480	09:20:00	11:00:00	2024-10-31	32	57
4481	09:20:00	11:00:00	2024-11-07	32	57
4482	09:20:00	11:00:00	2024-11-14	32	57
4483	09:20:00	11:00:00	2024-11-21	32	57
4484	09:20:00	11:00:00	2024-11-28	32	57
4485	09:20:00	11:00:00	2024-12-05	32	57
4486	09:20:00	11:00:00	2024-12-12	32	57
4525	09:20:00	11:00:00	2024-08-05	33	60
4526	09:20:00	11:00:00	2024-08-12	33	60
4527	09:20:00	11:00:00	2024-08-19	33	60
4528	09:20:00	11:00:00	2024-08-26	33	60
4529	09:20:00	11:00:00	2024-09-02	33	60
4530	09:20:00	11:00:00	2024-09-09	33	60
4531	09:20:00	11:00:00	2024-09-16	33	60
4532	09:20:00	11:00:00	2024-09-23	33	60
4533	09:20:00	11:00:00	2024-09-30	33	60
4534	09:20:00	11:00:00	2024-10-07	33	60
4535	09:20:00	11:00:00	2024-10-14	33	60
4536	09:20:00	11:00:00	2024-10-21	33	60
4537	09:20:00	11:00:00	2024-10-28	33	60
4538	09:20:00	11:00:00	2024-11-04	33	60
4539	09:20:00	11:00:00	2024-11-11	33	60
4540	09:20:00	11:00:00	2024-11-18	33	60
4541	09:20:00	11:00:00	2024-11-25	33	60
4542	09:20:00	11:00:00	2024-12-02	33	60
4543	09:20:00	11:00:00	2024-12-09	33	60
4544	09:20:00	11:00:00	2024-08-08	33	61
4545	09:20:00	11:00:00	2024-08-15	33	61
4546	09:20:00	11:00:00	2024-08-22	33	61
4547	09:20:00	11:00:00	2024-08-29	33	61
4548	09:20:00	11:00:00	2024-09-05	33	61
4549	09:20:00	11:00:00	2024-09-12	33	61
4550	09:20:00	11:00:00	2024-09-19	33	61
4551	09:20:00	11:00:00	2024-09-26	33	61
4552	09:20:00	11:00:00	2024-10-03	33	61
4553	09:20:00	11:00:00	2024-10-10	33	61
4554	09:20:00	11:00:00	2024-10-17	33	61
4555	09:20:00	11:00:00	2024-10-24	33	61
4556	09:20:00	11:00:00	2024-10-31	33	61
4557	09:20:00	11:00:00	2024-11-07	33	61
4558	09:20:00	11:00:00	2024-11-14	33	61
4559	09:20:00	11:00:00	2024-11-21	33	61
4560	09:20:00	11:00:00	2024-11-28	33	61
4561	09:20:00	11:00:00	2024-12-05	33	61
4562	09:20:00	11:00:00	2024-12-12	33	61
4600	07:30:00	09:10:00	2024-08-06	31	64
4601	07:30:00	09:10:00	2024-08-13	31	64
4602	07:30:00	09:10:00	2024-08-20	31	64
4603	07:30:00	09:10:00	2024-08-27	31	64
4604	07:30:00	09:10:00	2024-09-03	31	64
4605	07:30:00	09:10:00	2024-09-10	31	64
4606	07:30:00	09:10:00	2024-09-17	31	64
4607	07:30:00	09:10:00	2024-09-24	31	64
4608	07:30:00	09:10:00	2024-10-01	31	64
4609	07:30:00	09:10:00	2024-10-08	31	64
4610	07:30:00	09:10:00	2024-10-15	31	64
4611	07:30:00	09:10:00	2024-10-22	31	64
4612	07:30:00	09:10:00	2024-10-29	31	64
4613	07:30:00	09:10:00	2024-11-05	31	64
4614	07:30:00	09:10:00	2024-11-12	31	64
4615	07:30:00	09:10:00	2024-11-19	31	64
4616	07:30:00	09:10:00	2024-11-26	31	64
4617	07:30:00	09:10:00	2024-12-03	31	64
4618	07:30:00	09:10:00	2024-12-10	31	64
4619	07:30:00	09:10:00	2024-08-09	31	65
4620	07:30:00	09:10:00	2024-08-16	31	65
4621	07:30:00	09:10:00	2024-08-23	31	65
4622	07:30:00	09:10:00	2024-08-30	31	65
861	07:30:00	09:10:00	2024-08-07	32	265
862	07:30:00	09:10:00	2024-08-14	32	265
863	07:30:00	09:10:00	2024-08-21	32	265
864	07:30:00	09:10:00	2024-08-28	32	265
865	07:30:00	09:10:00	2024-09-04	32	265
866	07:30:00	09:10:00	2024-09-11	32	265
867	07:30:00	09:10:00	2024-09-18	32	265
868	07:30:00	09:10:00	2024-09-25	32	265
869	07:30:00	09:10:00	2024-10-02	32	265
870	07:30:00	09:10:00	2024-10-09	32	265
871	07:30:00	09:10:00	2024-10-16	32	265
872	07:30:00	09:10:00	2024-10-23	32	265
873	07:30:00	09:10:00	2024-10-30	32	265
874	07:30:00	09:10:00	2024-11-06	32	265
875	07:30:00	09:10:00	2024-11-13	32	265
876	07:30:00	09:10:00	2024-11-20	32	265
877	07:30:00	09:10:00	2024-11-27	32	265
878	07:30:00	09:10:00	2024-12-04	32	265
879	07:30:00	09:10:00	2024-12-11	32	265
880	09:20:00	11:00:00	2024-08-07	32	266
881	09:20:00	11:00:00	2024-08-14	32	266
882	09:20:00	11:00:00	2024-08-21	32	266
883	09:20:00	11:00:00	2024-08-28	32	266
884	09:20:00	11:00:00	2024-09-04	32	266
885	09:20:00	11:00:00	2024-09-11	32	266
886	09:20:00	11:00:00	2024-09-18	32	266
887	09:20:00	11:00:00	2024-09-25	32	266
888	09:20:00	11:00:00	2024-10-02	32	266
889	09:20:00	11:00:00	2024-10-09	32	266
890	09:20:00	11:00:00	2024-10-16	32	266
891	09:20:00	11:00:00	2024-10-23	32	266
892	09:20:00	11:00:00	2024-10-30	32	266
893	09:20:00	11:00:00	2024-11-06	32	266
894	09:20:00	11:00:00	2024-11-13	32	266
895	09:20:00	11:00:00	2024-11-20	32	266
896	09:20:00	11:00:00	2024-11-27	32	266
897	09:20:00	11:00:00	2024-12-04	32	266
898	09:20:00	11:00:00	2024-12-11	32	266
899	09:20:00	11:00:00	2024-08-07	32	267
900	09:20:00	11:00:00	2024-08-14	32	267
901	09:20:00	11:00:00	2024-08-21	32	267
902	09:20:00	11:00:00	2024-08-28	32	267
903	09:20:00	11:00:00	2024-09-04	32	267
904	09:20:00	11:00:00	2024-09-11	32	267
905	09:20:00	11:00:00	2024-09-18	32	267
906	09:20:00	11:00:00	2024-09-25	32	267
907	09:20:00	11:00:00	2024-10-02	32	267
908	09:20:00	11:00:00	2024-10-09	32	267
909	09:20:00	11:00:00	2024-10-16	32	267
910	09:20:00	11:00:00	2024-10-23	32	267
911	09:20:00	11:00:00	2024-10-30	32	267
912	09:20:00	11:00:00	2024-11-06	32	267
913	09:20:00	11:00:00	2024-11-13	32	267
914	09:20:00	11:00:00	2024-11-20	32	267
915	09:20:00	11:00:00	2024-11-27	32	267
916	09:20:00	11:00:00	2024-12-04	32	267
917	09:20:00	11:00:00	2024-12-11	32	267
918	13:10:00	14:50:00	2024-08-07	32	269
919	13:10:00	14:50:00	2024-08-14	32	269
920	13:10:00	14:50:00	2024-08-21	32	269
921	13:10:00	14:50:00	2024-08-28	32	269
922	13:10:00	14:50:00	2024-09-04	32	269
923	13:10:00	14:50:00	2024-09-11	32	269
924	13:10:00	14:50:00	2024-09-18	32	269
925	13:10:00	14:50:00	2024-09-25	32	269
926	13:10:00	14:50:00	2024-10-02	32	269
927	13:10:00	14:50:00	2024-10-09	32	269
928	13:10:00	14:50:00	2024-10-16	32	269
929	13:10:00	14:50:00	2024-10-23	32	269
930	13:10:00	14:50:00	2024-10-30	32	269
931	13:10:00	14:50:00	2024-11-06	32	269
932	13:10:00	14:50:00	2024-11-13	32	269
933	13:10:00	14:50:00	2024-11-20	32	269
934	13:10:00	14:50:00	2024-11-27	32	269
935	13:10:00	14:50:00	2024-12-04	32	269
936	13:10:00	14:50:00	2024-12-11	32	269
937	09:20:00	11:00:00	2024-08-07	69	268
938	09:20:00	11:00:00	2024-08-14	69	268
939	09:20:00	11:00:00	2024-08-21	69	268
940	09:20:00	11:00:00	2024-08-28	69	268
941	09:20:00	11:00:00	2024-09-04	69	268
942	09:20:00	11:00:00	2024-09-11	69	268
943	09:20:00	11:00:00	2024-09-18	69	268
944	09:20:00	11:00:00	2024-09-25	69	268
945	09:20:00	11:00:00	2024-10-02	69	268
946	09:20:00	11:00:00	2024-10-09	69	268
947	09:20:00	11:00:00	2024-10-16	69	268
948	09:20:00	11:00:00	2024-10-23	69	268
949	09:20:00	11:00:00	2024-10-30	69	268
950	09:20:00	11:00:00	2024-11-06	69	268
951	09:20:00	11:00:00	2024-11-13	69	268
952	09:20:00	11:00:00	2024-11-20	69	268
953	09:20:00	11:00:00	2024-11-27	69	268
954	09:20:00	11:00:00	2024-12-04	69	268
955	09:20:00	11:00:00	2024-12-11	69	268
956	13:10:00	14:50:00	2024-08-07	32	270
957	13:10:00	14:50:00	2024-08-14	32	270
958	13:10:00	14:50:00	2024-08-21	32	270
959	13:10:00	14:50:00	2024-08-28	32	270
960	13:10:00	14:50:00	2024-09-04	32	270
961	13:10:00	14:50:00	2024-09-11	32	270
962	13:10:00	14:50:00	2024-09-18	32	270
963	13:10:00	14:50:00	2024-09-25	32	270
964	13:10:00	14:50:00	2024-10-02	32	270
965	13:10:00	14:50:00	2024-10-09	32	270
966	13:10:00	14:50:00	2024-10-16	32	270
967	13:10:00	14:50:00	2024-10-23	32	270
968	13:10:00	14:50:00	2024-10-30	32	270
969	13:10:00	14:50:00	2024-11-06	32	270
970	13:10:00	14:50:00	2024-11-13	32	270
971	13:10:00	14:50:00	2024-11-20	32	270
972	13:10:00	14:50:00	2024-11-27	32	270
973	13:10:00	14:50:00	2024-12-04	32	270
974	13:10:00	14:50:00	2024-12-11	32	270
975	13:10:00	14:50:00	2024-08-08	32	271
976	13:10:00	14:50:00	2024-08-15	32	271
977	13:10:00	14:50:00	2024-08-22	32	271
978	13:10:00	14:50:00	2024-08-29	32	271
979	13:10:00	14:50:00	2024-09-05	32	271
980	13:10:00	14:50:00	2024-09-12	32	271
981	13:10:00	14:50:00	2024-09-19	32	271
982	13:10:00	14:50:00	2024-09-26	32	271
983	13:10:00	14:50:00	2024-10-03	32	271
984	13:10:00	14:50:00	2024-10-10	32	271
985	13:10:00	14:50:00	2024-10-17	32	271
986	13:10:00	14:50:00	2024-10-24	32	271
987	13:10:00	14:50:00	2024-10-31	32	271
988	13:10:00	14:50:00	2024-11-07	32	271
989	13:10:00	14:50:00	2024-11-14	32	271
990	13:10:00	14:50:00	2024-11-21	32	271
991	13:10:00	14:50:00	2024-11-28	32	271
992	13:10:00	14:50:00	2024-12-05	32	271
993	13:10:00	14:50:00	2024-12-12	32	271
1012	13:10:00	14:50:00	2024-08-09	32	272
1013	13:10:00	14:50:00	2024-08-16	32	272
1014	13:10:00	14:50:00	2024-08-23	32	272
1015	13:10:00	14:50:00	2024-08-30	32	272
1016	13:10:00	14:50:00	2024-09-06	32	272
1017	13:10:00	14:50:00	2024-09-13	32	272
1018	13:10:00	14:50:00	2024-09-20	32	272
1019	13:10:00	14:50:00	2024-09-27	32	272
1020	13:10:00	14:50:00	2024-10-04	32	272
1021	13:10:00	14:50:00	2024-10-11	32	272
1022	13:10:00	14:50:00	2024-10-18	32	272
1023	13:10:00	14:50:00	2024-10-25	32	272
1024	13:10:00	14:50:00	2024-11-01	32	272
1025	13:10:00	14:50:00	2024-11-08	32	272
1026	13:10:00	14:50:00	2024-11-15	32	272
1027	13:10:00	14:50:00	2024-11-22	32	272
1028	13:10:00	14:50:00	2024-11-29	32	272
1029	13:10:00	14:50:00	2024-12-06	32	272
4393	16:50:00	18:30:00	2024-08-05	35	53
4394	16:50:00	18:30:00	2024-08-12	35	53
4395	16:50:00	18:30:00	2024-08-19	35	53
4396	16:50:00	18:30:00	2024-08-26	35	53
4397	16:50:00	18:30:00	2024-09-02	35	53
4398	16:50:00	18:30:00	2024-09-09	35	53
4399	16:50:00	18:30:00	2024-09-16	35	53
4400	16:50:00	18:30:00	2024-09-23	35	53
4401	16:50:00	18:30:00	2024-09-30	35	53
4402	16:50:00	18:30:00	2024-10-07	35	53
4403	16:50:00	18:30:00	2024-10-14	35	53
4404	16:50:00	18:30:00	2024-10-21	35	53
4405	16:50:00	18:30:00	2024-10-28	35	53
4406	16:50:00	18:30:00	2024-11-04	35	53
4407	16:50:00	18:30:00	2024-11-11	35	53
4408	16:50:00	18:30:00	2024-11-18	35	53
4409	16:50:00	18:30:00	2024-11-25	35	53
4410	16:50:00	18:30:00	2024-12-02	35	53
4411	16:50:00	18:30:00	2024-12-09	35	53
4412	16:50:00	18:30:00	2024-08-08	27	54
4413	16:50:00	18:30:00	2024-08-15	27	54
4414	16:50:00	18:30:00	2024-08-22	27	54
4415	16:50:00	18:30:00	2024-08-29	27	54
4416	16:50:00	18:30:00	2024-09-05	27	54
4417	16:50:00	18:30:00	2024-09-12	27	54
4418	16:50:00	18:30:00	2024-09-19	27	54
4419	16:50:00	18:30:00	2024-09-26	27	54
4420	16:50:00	18:30:00	2024-10-03	27	54
4421	16:50:00	18:30:00	2024-10-10	27	54
4422	16:50:00	18:30:00	2024-10-17	27	54
4423	16:50:00	18:30:00	2024-10-24	27	54
4424	16:50:00	18:30:00	2024-10-31	27	54
4425	16:50:00	18:30:00	2024-11-07	27	54
4426	16:50:00	18:30:00	2024-11-14	27	54
4427	16:50:00	18:30:00	2024-11-21	27	54
4428	16:50:00	18:30:00	2024-11-28	27	54
4429	16:50:00	18:30:00	2024-12-05	27	54
4430	16:50:00	18:30:00	2024-12-12	27	54
4431	11:20:00	12:10:00	2024-08-10	68	55
4432	11:20:00	12:10:00	2024-08-17	68	55
4433	11:20:00	12:10:00	2024-08-24	68	55
4434	11:20:00	12:10:00	2024-08-31	68	55
4435	11:20:00	12:10:00	2024-09-07	68	55
4436	11:20:00	12:10:00	2024-09-14	68	55
4437	11:20:00	12:10:00	2024-09-21	68	55
4438	11:20:00	12:10:00	2024-09-28	68	55
4439	11:20:00	12:10:00	2024-10-05	68	55
4440	11:20:00	12:10:00	2024-10-12	68	55
4441	11:20:00	12:10:00	2024-10-19	68	55
4442	11:20:00	12:10:00	2024-10-26	68	55
4443	11:20:00	12:10:00	2024-11-02	68	55
4444	11:20:00	12:10:00	2024-11-09	68	55
4445	11:20:00	12:10:00	2024-11-16	68	55
4446	11:20:00	12:10:00	2024-11-23	68	55
4447	11:20:00	12:10:00	2024-11-30	68	55
4448	11:20:00	12:10:00	2024-12-07	68	55
4487	09:20:00	11:00:00	2024-08-05	31	58
4488	09:20:00	11:00:00	2024-08-12	31	58
4489	09:20:00	11:00:00	2024-08-19	31	58
4490	09:20:00	11:00:00	2024-08-26	31	58
4491	09:20:00	11:00:00	2024-09-02	31	58
4492	09:20:00	11:00:00	2024-09-09	31	58
4493	09:20:00	11:00:00	2024-09-16	31	58
4494	09:20:00	11:00:00	2024-09-23	31	58
4495	09:20:00	11:00:00	2024-09-30	31	58
4496	09:20:00	11:00:00	2024-10-07	31	58
4497	09:20:00	11:00:00	2024-10-14	31	58
4498	09:20:00	11:00:00	2024-10-21	31	58
4499	09:20:00	11:00:00	2024-10-28	31	58
4500	09:20:00	11:00:00	2024-11-04	31	58
4501	09:20:00	11:00:00	2024-11-11	31	58
4502	09:20:00	11:00:00	2024-11-18	31	58
4503	09:20:00	11:00:00	2024-11-25	31	58
4504	09:20:00	11:00:00	2024-12-02	31	58
4505	09:20:00	11:00:00	2024-12-09	31	58
4506	09:20:00	11:00:00	2024-08-08	31	59
4507	09:20:00	11:00:00	2024-08-15	31	59
4508	09:20:00	11:00:00	2024-08-22	31	59
4509	09:20:00	11:00:00	2024-08-29	31	59
4510	09:20:00	11:00:00	2024-09-05	31	59
4511	09:20:00	11:00:00	2024-09-12	31	59
4512	09:20:00	11:00:00	2024-09-19	31	59
4513	09:20:00	11:00:00	2024-09-26	31	59
4514	09:20:00	11:00:00	2024-10-03	31	59
4515	09:20:00	11:00:00	2024-10-10	31	59
4516	09:20:00	11:00:00	2024-10-17	31	59
4517	09:20:00	11:00:00	2024-10-24	31	59
4518	09:20:00	11:00:00	2024-10-31	31	59
4519	09:20:00	11:00:00	2024-11-07	31	59
994	13:10:00	14:50:00	2024-08-09	32	274
995	13:10:00	14:50:00	2024-08-16	32	274
996	13:10:00	14:50:00	2024-08-23	32	274
997	13:10:00	14:50:00	2024-08-30	32	274
998	13:10:00	14:50:00	2024-09-06	32	274
999	13:10:00	14:50:00	2024-09-13	32	274
1000	13:10:00	14:50:00	2024-09-20	32	274
1001	13:10:00	14:50:00	2024-09-27	32	274
1002	13:10:00	14:50:00	2024-10-04	32	274
1003	13:10:00	14:50:00	2024-10-11	32	274
1004	13:10:00	14:50:00	2024-10-18	32	274
1005	13:10:00	14:50:00	2024-10-25	32	274
1006	13:10:00	14:50:00	2024-11-01	32	274
1007	13:10:00	14:50:00	2024-11-08	32	274
1008	13:10:00	14:50:00	2024-11-15	32	274
1009	13:10:00	14:50:00	2024-11-22	32	274
1010	13:10:00	14:50:00	2024-11-29	32	274
1011	13:10:00	14:50:00	2024-12-06	32	274
1030	09:20:00	11:00:00	2024-08-05	16	276
1031	09:20:00	11:00:00	2024-08-12	16	276
1032	09:20:00	11:00:00	2024-08-19	16	276
1033	09:20:00	11:00:00	2024-08-26	16	276
1034	09:20:00	11:00:00	2024-09-02	16	276
1035	09:20:00	11:00:00	2024-09-09	16	276
1036	09:20:00	11:00:00	2024-09-16	16	276
1037	09:20:00	11:00:00	2024-09-23	16	276
1038	09:20:00	11:00:00	2024-09-30	16	276
1039	09:20:00	11:00:00	2024-10-07	16	276
1040	09:20:00	11:00:00	2024-10-14	16	276
1041	09:20:00	11:00:00	2024-10-21	16	276
1042	09:20:00	11:00:00	2024-10-28	16	276
1043	09:20:00	11:00:00	2024-11-04	16	276
1044	09:20:00	11:00:00	2024-11-11	16	276
1045	09:20:00	11:00:00	2024-11-18	16	276
1046	09:20:00	11:00:00	2024-11-25	16	276
1047	09:20:00	11:00:00	2024-12-02	16	276
1048	09:20:00	11:00:00	2024-12-09	16	276
1049	07:30:00	09:10:00	2024-08-08	16	277
1050	07:30:00	09:10:00	2024-08-15	16	277
1051	07:30:00	09:10:00	2024-08-22	16	277
1052	07:30:00	09:10:00	2024-08-29	16	277
1053	07:30:00	09:10:00	2024-09-05	16	277
1054	07:30:00	09:10:00	2024-09-12	16	277
1055	07:30:00	09:10:00	2024-09-19	16	277
1056	07:30:00	09:10:00	2024-09-26	16	277
1057	07:30:00	09:10:00	2024-10-03	16	277
1058	07:30:00	09:10:00	2024-10-10	16	277
1059	07:30:00	09:10:00	2024-10-17	16	277
1060	07:30:00	09:10:00	2024-10-24	16	277
1061	07:30:00	09:10:00	2024-10-31	16	277
1062	07:30:00	09:10:00	2024-11-07	16	277
1063	07:30:00	09:10:00	2024-11-14	16	277
1064	07:30:00	09:10:00	2024-11-21	16	277
1065	07:30:00	09:10:00	2024-11-28	16	277
1066	07:30:00	09:10:00	2024-12-05	16	277
1067	07:30:00	09:10:00	2024-12-12	16	277
1068	13:10:00	14:50:00	2024-08-05	16	278
1069	13:10:00	14:50:00	2024-08-12	16	278
1070	13:10:00	14:50:00	2024-08-19	16	278
1071	13:10:00	14:50:00	2024-08-26	16	278
1072	13:10:00	14:50:00	2024-09-02	16	278
1073	13:10:00	14:50:00	2024-09-09	16	278
1074	13:10:00	14:50:00	2024-09-16	16	278
1075	13:10:00	14:50:00	2024-09-23	16	278
1076	13:10:00	14:50:00	2024-09-30	16	278
1077	13:10:00	14:50:00	2024-10-07	16	278
1078	13:10:00	14:50:00	2024-10-14	16	278
1079	13:10:00	14:50:00	2024-10-21	16	278
1080	13:10:00	14:50:00	2024-10-28	16	278
1081	13:10:00	14:50:00	2024-11-04	16	278
1082	13:10:00	14:50:00	2024-11-11	16	278
1083	13:10:00	14:50:00	2024-11-18	16	278
1084	13:10:00	14:50:00	2024-11-25	16	278
1085	13:10:00	14:50:00	2024-12-02	16	278
1086	13:10:00	14:50:00	2024-12-09	16	278
1087	15:00:00	16:40:00	2024-08-08	16	279
1088	15:00:00	16:40:00	2024-08-15	16	279
1089	15:00:00	16:40:00	2024-08-22	16	279
1090	15:00:00	16:40:00	2024-08-29	16	279
1091	15:00:00	16:40:00	2024-09-05	16	279
1092	15:00:00	16:40:00	2024-09-12	16	279
1093	15:00:00	16:40:00	2024-09-19	16	279
1094	15:00:00	16:40:00	2024-09-26	16	279
1095	15:00:00	16:40:00	2024-10-03	16	279
1096	15:00:00	16:40:00	2024-10-10	16	279
1097	15:00:00	16:40:00	2024-10-17	16	279
1098	15:00:00	16:40:00	2024-10-24	16	279
1099	15:00:00	16:40:00	2024-10-31	16	279
1100	15:00:00	16:40:00	2024-11-07	16	279
1101	15:00:00	16:40:00	2024-11-14	16	279
1102	15:00:00	16:40:00	2024-11-21	16	279
1103	15:00:00	16:40:00	2024-11-28	16	279
1104	15:00:00	16:40:00	2024-12-05	16	279
1105	15:00:00	16:40:00	2024-12-12	16	279
1106	15:00:00	16:40:00	2024-08-05	17	280
1107	15:00:00	16:40:00	2024-08-12	17	280
1108	15:00:00	16:40:00	2024-08-19	17	280
1109	15:00:00	16:40:00	2024-08-26	17	280
1110	15:00:00	16:40:00	2024-09-02	17	280
1111	15:00:00	16:40:00	2024-09-09	17	280
1112	15:00:00	16:40:00	2024-09-16	17	280
1113	15:00:00	16:40:00	2024-09-23	17	280
1114	15:00:00	16:40:00	2024-09-30	17	280
1115	15:00:00	16:40:00	2024-10-07	17	280
1116	15:00:00	16:40:00	2024-10-14	17	280
1117	15:00:00	16:40:00	2024-10-21	17	280
1118	15:00:00	16:40:00	2024-10-28	17	280
1119	15:00:00	16:40:00	2024-11-04	17	280
1120	15:00:00	16:40:00	2024-11-11	17	280
1121	15:00:00	16:40:00	2024-11-18	17	280
1122	15:00:00	16:40:00	2024-11-25	17	280
1123	15:00:00	16:40:00	2024-12-02	17	280
1124	15:00:00	16:40:00	2024-12-09	17	280
1125	13:10:00	14:50:00	2024-08-08	17	281
1126	13:10:00	14:50:00	2024-08-15	17	281
1127	13:10:00	14:50:00	2024-08-22	17	281
1128	13:10:00	14:50:00	2024-08-29	17	281
1129	13:10:00	14:50:00	2024-09-05	17	281
1130	13:10:00	14:50:00	2024-09-12	17	281
1131	13:10:00	14:50:00	2024-09-19	17	281
1132	13:10:00	14:50:00	2024-09-26	17	281
1133	13:10:00	14:50:00	2024-10-03	17	281
1134	13:10:00	14:50:00	2024-10-10	17	281
1135	13:10:00	14:50:00	2024-10-17	17	281
1136	13:10:00	14:50:00	2024-10-24	17	281
1137	13:10:00	14:50:00	2024-10-31	17	281
1138	13:10:00	14:50:00	2024-11-07	17	281
1139	13:10:00	14:50:00	2024-11-14	17	281
1140	13:10:00	14:50:00	2024-11-21	17	281
1141	13:10:00	14:50:00	2024-11-28	17	281
1142	13:10:00	14:50:00	2024-12-05	17	281
1143	13:10:00	14:50:00	2024-12-12	17	281
1144	07:30:00	09:10:00	2024-08-05	17	282
1145	07:30:00	09:10:00	2024-08-12	17	282
1146	07:30:00	09:10:00	2024-08-19	17	282
1147	07:30:00	09:10:00	2024-08-26	17	282
1148	07:30:00	09:10:00	2024-09-02	17	282
1149	07:30:00	09:10:00	2024-09-09	17	282
1150	07:30:00	09:10:00	2024-09-16	17	282
1151	07:30:00	09:10:00	2024-09-23	17	282
1152	07:30:00	09:10:00	2024-09-30	17	282
1153	07:30:00	09:10:00	2024-10-07	17	282
1154	07:30:00	09:10:00	2024-10-14	17	282
1155	07:30:00	09:10:00	2024-10-21	17	282
1156	07:30:00	09:10:00	2024-10-28	17	282
1157	07:30:00	09:10:00	2024-11-04	17	282
1158	07:30:00	09:10:00	2024-11-11	17	282
1159	07:30:00	09:10:00	2024-11-18	17	282
1160	07:30:00	09:10:00	2024-11-25	17	282
1161	07:30:00	09:10:00	2024-12-02	17	282
1162	07:30:00	09:10:00	2024-12-09	17	282
1163	09:20:00	11:00:00	2024-08-08	17	283
1164	09:20:00	11:00:00	2024-08-15	17	283
1165	09:20:00	11:00:00	2024-08-22	17	283
1166	09:20:00	11:00:00	2024-08-29	17	283
1167	09:20:00	11:00:00	2024-09-05	17	283
1168	09:20:00	11:00:00	2024-09-12	17	283
1169	09:20:00	11:00:00	2024-09-19	17	283
1170	09:20:00	11:00:00	2024-09-26	17	283
1171	09:20:00	11:00:00	2024-10-03	17	283
1172	09:20:00	11:00:00	2024-10-10	17	283
1173	09:20:00	11:00:00	2024-10-17	17	283
1174	09:20:00	11:00:00	2024-10-24	17	283
1175	09:20:00	11:00:00	2024-10-31	17	283
1176	09:20:00	11:00:00	2024-11-07	17	283
1177	09:20:00	11:00:00	2024-11-14	17	283
1178	09:20:00	11:00:00	2024-11-21	17	283
1179	09:20:00	11:00:00	2024-11-28	17	283
1180	09:20:00	11:00:00	2024-12-05	17	283
1181	09:20:00	11:00:00	2024-12-12	17	283
1182	09:20:00	11:00:00	2024-08-05	18	284
1183	09:20:00	11:00:00	2024-08-12	18	284
1184	09:20:00	11:00:00	2024-08-19	18	284
1185	09:20:00	11:00:00	2024-08-26	18	284
1186	09:20:00	11:00:00	2024-09-02	18	284
1187	09:20:00	11:00:00	2024-09-09	18	284
1188	09:20:00	11:00:00	2024-09-16	18	284
1189	09:20:00	11:00:00	2024-09-23	18	284
1190	09:20:00	11:00:00	2024-09-30	18	284
1191	09:20:00	11:00:00	2024-10-07	18	284
1192	09:20:00	11:00:00	2024-10-14	18	284
1193	09:20:00	11:00:00	2024-10-21	18	284
1194	09:20:00	11:00:00	2024-10-28	18	284
1195	09:20:00	11:00:00	2024-11-04	18	284
1196	09:20:00	11:00:00	2024-11-11	18	284
1197	09:20:00	11:00:00	2024-11-18	18	284
1198	09:20:00	11:00:00	2024-11-25	18	284
1199	09:20:00	11:00:00	2024-12-02	18	284
1200	09:20:00	11:00:00	2024-12-09	18	284
1201	07:30:00	09:10:00	2024-08-08	18	285
1202	07:30:00	09:10:00	2024-08-15	18	285
1203	07:30:00	09:10:00	2024-08-22	18	285
1204	07:30:00	09:10:00	2024-08-29	18	285
1205	07:30:00	09:10:00	2024-09-05	18	285
1206	07:30:00	09:10:00	2024-09-12	18	285
1207	07:30:00	09:10:00	2024-09-19	18	285
1208	07:30:00	09:10:00	2024-09-26	18	285
1209	07:30:00	09:10:00	2024-10-03	18	285
1210	07:30:00	09:10:00	2024-10-10	18	285
1211	07:30:00	09:10:00	2024-10-17	18	285
1212	07:30:00	09:10:00	2024-10-24	18	285
1213	07:30:00	09:10:00	2024-10-31	18	285
1214	07:30:00	09:10:00	2024-11-07	18	285
1215	07:30:00	09:10:00	2024-11-14	18	285
1216	07:30:00	09:10:00	2024-11-21	18	285
1217	07:30:00	09:10:00	2024-11-28	18	285
1218	07:30:00	09:10:00	2024-12-05	18	285
1219	07:30:00	09:10:00	2024-12-12	18	285
1220	07:30:00	09:10:00	2024-08-05	69	286
1221	07:30:00	09:10:00	2024-08-12	69	286
1222	07:30:00	09:10:00	2024-08-19	69	286
1223	07:30:00	09:10:00	2024-08-26	69	286
1224	07:30:00	09:10:00	2024-09-02	69	286
1225	07:30:00	09:10:00	2024-09-09	69	286
1226	07:30:00	09:10:00	2024-09-16	69	286
1227	07:30:00	09:10:00	2024-09-23	69	286
1228	07:30:00	09:10:00	2024-09-30	69	286
1229	07:30:00	09:10:00	2024-10-07	69	286
1230	07:30:00	09:10:00	2024-10-14	69	286
1231	07:30:00	09:10:00	2024-10-21	69	286
1232	07:30:00	09:10:00	2024-10-28	69	286
1233	07:30:00	09:10:00	2024-11-04	69	286
1234	07:30:00	09:10:00	2024-11-11	69	286
1235	07:30:00	09:10:00	2024-11-18	69	286
1236	07:30:00	09:10:00	2024-11-25	69	286
1237	07:30:00	09:10:00	2024-12-02	69	286
1238	07:30:00	09:10:00	2024-12-09	69	286
1239	09:20:00	11:00:00	2024-08-08	69	287
1240	09:20:00	11:00:00	2024-08-15	69	287
1241	09:20:00	11:00:00	2024-08-22	69	287
1242	09:20:00	11:00:00	2024-08-29	69	287
1243	09:20:00	11:00:00	2024-09-05	69	287
1244	09:20:00	11:00:00	2024-09-12	69	287
1245	09:20:00	11:00:00	2024-09-19	69	287
1246	09:20:00	11:00:00	2024-09-26	69	287
1247	09:20:00	11:00:00	2024-10-03	69	287
1248	09:20:00	11:00:00	2024-10-10	69	287
1249	09:20:00	11:00:00	2024-10-17	69	287
1250	09:20:00	11:00:00	2024-10-24	69	287
1251	09:20:00	11:00:00	2024-10-31	69	287
1252	09:20:00	11:00:00	2024-11-07	69	287
1253	09:20:00	11:00:00	2024-11-14	69	287
1254	09:20:00	11:00:00	2024-11-21	69	287
1255	09:20:00	11:00:00	2024-11-28	69	287
1256	09:20:00	11:00:00	2024-12-05	69	287
1257	09:20:00	11:00:00	2024-12-12	69	287
1258	09:20:00	11:00:00	2024-08-05	20	288
1259	09:20:00	11:00:00	2024-08-12	20	288
1260	09:20:00	11:00:00	2024-08-19	20	288
1261	09:20:00	11:00:00	2024-08-26	20	288
1262	09:20:00	11:00:00	2024-09-02	20	288
1263	09:20:00	11:00:00	2024-09-09	20	288
1264	09:20:00	11:00:00	2024-09-16	20	288
1265	09:20:00	11:00:00	2024-09-23	20	288
1266	09:20:00	11:00:00	2024-09-30	20	288
1267	09:20:00	11:00:00	2024-10-07	20	288
1268	09:20:00	11:00:00	2024-10-14	20	288
1269	09:20:00	11:00:00	2024-10-21	20	288
1270	09:20:00	11:00:00	2024-10-28	20	288
1271	09:20:00	11:00:00	2024-11-04	20	288
1272	09:20:00	11:00:00	2024-11-11	20	288
1273	09:20:00	11:00:00	2024-11-18	20	288
1274	09:20:00	11:00:00	2024-11-25	20	288
1275	09:20:00	11:00:00	2024-12-02	20	288
1276	09:20:00	11:00:00	2024-12-09	20	288
1277	07:30:00	09:10:00	2024-08-07	20	289
1278	07:30:00	09:10:00	2024-08-14	20	289
1279	07:30:00	09:10:00	2024-08-21	20	289
1280	07:30:00	09:10:00	2024-08-28	20	289
1281	07:30:00	09:10:00	2024-09-04	20	289
1282	07:30:00	09:10:00	2024-09-11	20	289
1283	07:30:00	09:10:00	2024-09-18	20	289
1284	07:30:00	09:10:00	2024-09-25	20	289
1285	07:30:00	09:10:00	2024-10-02	20	289
1286	07:30:00	09:10:00	2024-10-09	20	289
1287	07:30:00	09:10:00	2024-10-16	20	289
1288	07:30:00	09:10:00	2024-10-23	20	289
1289	07:30:00	09:10:00	2024-10-30	20	289
1290	07:30:00	09:10:00	2024-11-06	20	289
1291	07:30:00	09:10:00	2024-11-13	20	289
1292	07:30:00	09:10:00	2024-11-20	20	289
1293	07:30:00	09:10:00	2024-11-27	20	289
1294	07:30:00	09:10:00	2024-12-04	20	289
1295	07:30:00	09:10:00	2024-12-11	20	289
1296	07:30:00	09:10:00	2024-08-06	17	290
1297	07:30:00	09:10:00	2024-08-13	17	290
1298	07:30:00	09:10:00	2024-08-20	17	290
1299	07:30:00	09:10:00	2024-08-27	17	290
1300	07:30:00	09:10:00	2024-09-03	17	290
1301	07:30:00	09:10:00	2024-09-10	17	290
1302	07:30:00	09:10:00	2024-09-17	17	290
1303	07:30:00	09:10:00	2024-09-24	17	290
1304	07:30:00	09:10:00	2024-10-01	17	290
1305	07:30:00	09:10:00	2024-10-08	17	290
1306	07:30:00	09:10:00	2024-10-15	17	290
1307	07:30:00	09:10:00	2024-10-22	17	290
1308	07:30:00	09:10:00	2024-10-29	17	290
1309	07:30:00	09:10:00	2024-11-05	17	290
1310	07:30:00	09:10:00	2024-11-12	17	290
1311	07:30:00	09:10:00	2024-11-19	17	290
1312	07:30:00	09:10:00	2024-11-26	17	290
1313	07:30:00	09:10:00	2024-12-03	17	290
1314	07:30:00	09:10:00	2024-12-10	17	290
1315	09:20:00	11:00:00	2024-08-09	17	291
1316	09:20:00	11:00:00	2024-08-16	17	291
1317	09:20:00	11:00:00	2024-08-23	17	291
1318	09:20:00	11:00:00	2024-08-30	17	291
1319	09:20:00	11:00:00	2024-09-06	17	291
1320	09:20:00	11:00:00	2024-09-13	17	291
1321	09:20:00	11:00:00	2024-09-20	17	291
1322	09:20:00	11:00:00	2024-09-27	17	291
1323	09:20:00	11:00:00	2024-10-04	17	291
1324	09:20:00	11:00:00	2024-10-11	17	291
1325	09:20:00	11:00:00	2024-10-18	17	291
1326	09:20:00	11:00:00	2024-10-25	17	291
1327	09:20:00	11:00:00	2024-11-01	17	291
1328	09:20:00	11:00:00	2024-11-08	17	291
1329	09:20:00	11:00:00	2024-11-15	17	291
1330	09:20:00	11:00:00	2024-11-22	17	291
1331	09:20:00	11:00:00	2024-11-29	17	291
1332	09:20:00	11:00:00	2024-12-06	17	291
1333	09:20:00	11:00:00	2024-08-06	16	292
1334	09:20:00	11:00:00	2024-08-13	16	292
1335	09:20:00	11:00:00	2024-08-20	16	292
1336	09:20:00	11:00:00	2024-08-27	16	292
1337	09:20:00	11:00:00	2024-09-03	16	292
1338	09:20:00	11:00:00	2024-09-10	16	292
1339	09:20:00	11:00:00	2024-09-17	16	292
1340	09:20:00	11:00:00	2024-09-24	16	292
1341	09:20:00	11:00:00	2024-10-01	16	292
1342	09:20:00	11:00:00	2024-10-08	16	292
1343	09:20:00	11:00:00	2024-10-15	16	292
1344	09:20:00	11:00:00	2024-10-22	16	292
1345	09:20:00	11:00:00	2024-10-29	16	292
1346	09:20:00	11:00:00	2024-11-05	16	292
1347	09:20:00	11:00:00	2024-11-12	16	292
1348	09:20:00	11:00:00	2024-11-19	16	292
1349	09:20:00	11:00:00	2024-11-26	16	292
1350	09:20:00	11:00:00	2024-12-03	16	292
1351	09:20:00	11:00:00	2024-12-10	16	292
1352	07:30:00	09:10:00	2024-08-09	16	293
1353	07:30:00	09:10:00	2024-08-16	16	293
1354	07:30:00	09:10:00	2024-08-23	16	293
1355	07:30:00	09:10:00	2024-08-30	16	293
1356	07:30:00	09:10:00	2024-09-06	16	293
1357	07:30:00	09:10:00	2024-09-13	16	293
1358	07:30:00	09:10:00	2024-09-20	16	293
1359	07:30:00	09:10:00	2024-09-27	16	293
1360	07:30:00	09:10:00	2024-10-04	16	293
1361	07:30:00	09:10:00	2024-10-11	16	293
1362	07:30:00	09:10:00	2024-10-18	16	293
1363	07:30:00	09:10:00	2024-10-25	16	293
1364	07:30:00	09:10:00	2024-11-01	16	293
1365	07:30:00	09:10:00	2024-11-08	16	293
1366	07:30:00	09:10:00	2024-11-15	16	293
1367	07:30:00	09:10:00	2024-11-22	16	293
1368	07:30:00	09:10:00	2024-11-29	16	293
1369	07:30:00	09:10:00	2024-12-06	16	293
1370	15:00:00	16:40:00	2024-08-06	18	294
1371	15:00:00	16:40:00	2024-08-13	18	294
1372	15:00:00	16:40:00	2024-08-20	18	294
1373	15:00:00	16:40:00	2024-08-27	18	294
1374	15:00:00	16:40:00	2024-09-03	18	294
1375	15:00:00	16:40:00	2024-09-10	18	294
1376	15:00:00	16:40:00	2024-09-17	18	294
1377	15:00:00	16:40:00	2024-09-24	18	294
1378	15:00:00	16:40:00	2024-10-01	18	294
1379	15:00:00	16:40:00	2024-10-08	18	294
1380	15:00:00	16:40:00	2024-10-15	18	294
1381	15:00:00	16:40:00	2024-10-22	18	294
1382	15:00:00	16:40:00	2024-10-29	18	294
1383	15:00:00	16:40:00	2024-11-05	18	294
1384	15:00:00	16:40:00	2024-11-12	18	294
1385	15:00:00	16:40:00	2024-11-19	18	294
1386	15:00:00	16:40:00	2024-11-26	18	294
1387	15:00:00	16:40:00	2024-12-03	18	294
1388	15:00:00	16:40:00	2024-12-10	18	294
1389	07:30:00	09:10:00	2024-08-09	18	295
1390	07:30:00	09:10:00	2024-08-16	18	295
1391	07:30:00	09:10:00	2024-08-23	18	295
1392	07:30:00	09:10:00	2024-08-30	18	295
1393	07:30:00	09:10:00	2024-09-06	18	295
1394	07:30:00	09:10:00	2024-09-13	18	295
1395	07:30:00	09:10:00	2024-09-20	18	295
1396	07:30:00	09:10:00	2024-09-27	18	295
1397	07:30:00	09:10:00	2024-10-04	18	295
1398	07:30:00	09:10:00	2024-10-11	18	295
1399	07:30:00	09:10:00	2024-10-18	18	295
1400	07:30:00	09:10:00	2024-10-25	18	295
1401	07:30:00	09:10:00	2024-11-01	18	295
1402	07:30:00	09:10:00	2024-11-08	18	295
1403	07:30:00	09:10:00	2024-11-15	18	295
1404	07:30:00	09:10:00	2024-11-22	18	295
1405	07:30:00	09:10:00	2024-11-29	18	295
1406	07:30:00	09:10:00	2024-12-06	18	295
1407	07:30:00	09:10:00	2024-08-05	19	298
1408	07:30:00	09:10:00	2024-08-12	19	298
1409	07:30:00	09:10:00	2024-08-19	19	298
1410	07:30:00	09:10:00	2024-08-26	19	298
1411	07:30:00	09:10:00	2024-09-02	19	298
1412	07:30:00	09:10:00	2024-09-09	19	298
1413	07:30:00	09:10:00	2024-09-16	19	298
1414	07:30:00	09:10:00	2024-09-23	19	298
1415	07:30:00	09:10:00	2024-09-30	19	298
1416	07:30:00	09:10:00	2024-10-07	19	298
1417	07:30:00	09:10:00	2024-10-14	19	298
1418	07:30:00	09:10:00	2024-10-21	19	298
1419	07:30:00	09:10:00	2024-10-28	19	298
1420	07:30:00	09:10:00	2024-11-04	19	298
1421	07:30:00	09:10:00	2024-11-11	19	298
1422	07:30:00	09:10:00	2024-11-18	19	298
1423	07:30:00	09:10:00	2024-11-25	19	298
1424	07:30:00	09:10:00	2024-12-02	19	298
1425	07:30:00	09:10:00	2024-12-09	19	298
1426	09:20:00	11:00:00	2024-08-07	19	299
1427	09:20:00	11:00:00	2024-08-14	19	299
1428	09:20:00	11:00:00	2024-08-21	19	299
1429	09:20:00	11:00:00	2024-08-28	19	299
1430	09:20:00	11:00:00	2024-09-04	19	299
1431	09:20:00	11:00:00	2024-09-11	19	299
1432	09:20:00	11:00:00	2024-09-18	19	299
1433	09:20:00	11:00:00	2024-09-25	19	299
1434	09:20:00	11:00:00	2024-10-02	19	299
1435	09:20:00	11:00:00	2024-10-09	19	299
1436	09:20:00	11:00:00	2024-10-16	19	299
1437	09:20:00	11:00:00	2024-10-23	19	299
1438	09:20:00	11:00:00	2024-10-30	19	299
1439	09:20:00	11:00:00	2024-11-06	19	299
1440	09:20:00	11:00:00	2024-11-13	19	299
1441	09:20:00	11:00:00	2024-11-20	19	299
1442	09:20:00	11:00:00	2024-11-27	19	299
1443	09:20:00	11:00:00	2024-12-04	19	299
1444	09:20:00	11:00:00	2024-12-11	19	299
1445	13:10:00	14:50:00	2024-08-06	11	320
1446	13:10:00	14:50:00	2024-08-13	11	320
1447	13:10:00	14:50:00	2024-08-20	11	320
1448	13:10:00	14:50:00	2024-08-27	11	320
1449	13:10:00	14:50:00	2024-09-03	11	320
1450	13:10:00	14:50:00	2024-09-10	11	320
1451	13:10:00	14:50:00	2024-09-17	11	320
1452	13:10:00	14:50:00	2024-09-24	11	320
1453	13:10:00	14:50:00	2024-10-01	11	320
1454	13:10:00	14:50:00	2024-10-08	11	320
1455	13:10:00	14:50:00	2024-10-15	11	320
1456	13:10:00	14:50:00	2024-10-22	11	320
1457	13:10:00	14:50:00	2024-10-29	11	320
1458	13:10:00	14:50:00	2024-11-05	11	320
1459	13:10:00	14:50:00	2024-11-12	11	320
1460	13:10:00	14:50:00	2024-11-19	11	320
1461	13:10:00	14:50:00	2024-11-26	11	320
1462	13:10:00	14:50:00	2024-12-03	11	320
1463	13:10:00	14:50:00	2024-12-10	11	320
1464	15:00:00	16:40:00	2024-08-08	11	321
1465	15:00:00	16:40:00	2024-08-15	11	321
1466	15:00:00	16:40:00	2024-08-22	11	321
1467	15:00:00	16:40:00	2024-08-29	11	321
1468	15:00:00	16:40:00	2024-09-05	11	321
1469	15:00:00	16:40:00	2024-09-12	11	321
1470	15:00:00	16:40:00	2024-09-19	11	321
1471	15:00:00	16:40:00	2024-09-26	11	321
1472	15:00:00	16:40:00	2024-10-03	11	321
1473	15:00:00	16:40:00	2024-10-10	11	321
1474	15:00:00	16:40:00	2024-10-17	11	321
1475	15:00:00	16:40:00	2024-10-24	11	321
1476	15:00:00	16:40:00	2024-10-31	11	321
1477	15:00:00	16:40:00	2024-11-07	11	321
1478	15:00:00	16:40:00	2024-11-14	11	321
1479	15:00:00	16:40:00	2024-11-21	11	321
1480	15:00:00	16:40:00	2024-11-28	11	321
1481	15:00:00	16:40:00	2024-12-05	11	321
1482	15:00:00	16:40:00	2024-12-12	11	321
1483	15:00:00	16:40:00	2024-08-06	12	322
1484	15:00:00	16:40:00	2024-08-13	12	322
1485	15:00:00	16:40:00	2024-08-20	12	322
1486	15:00:00	16:40:00	2024-08-27	12	322
1487	15:00:00	16:40:00	2024-09-03	12	322
1488	15:00:00	16:40:00	2024-09-10	12	322
1489	15:00:00	16:40:00	2024-09-17	12	322
1490	15:00:00	16:40:00	2024-09-24	12	322
1491	15:00:00	16:40:00	2024-10-01	12	322
1492	15:00:00	16:40:00	2024-10-08	12	322
1493	15:00:00	16:40:00	2024-10-15	12	322
1494	15:00:00	16:40:00	2024-10-22	12	322
1495	15:00:00	16:40:00	2024-10-29	12	322
1496	15:00:00	16:40:00	2024-11-05	12	322
1497	15:00:00	16:40:00	2024-11-12	12	322
1498	15:00:00	16:40:00	2024-11-19	12	322
1499	15:00:00	16:40:00	2024-11-26	12	322
1500	15:00:00	16:40:00	2024-12-03	12	322
1501	15:00:00	16:40:00	2024-12-10	12	322
1502	13:10:00	14:50:00	2024-08-08	12	323
1503	13:10:00	14:50:00	2024-08-15	12	323
1504	13:10:00	14:50:00	2024-08-22	12	323
1505	13:10:00	14:50:00	2024-08-29	12	323
1506	13:10:00	14:50:00	2024-09-05	12	323
1507	13:10:00	14:50:00	2024-09-12	12	323
1508	13:10:00	14:50:00	2024-09-19	12	323
1509	13:10:00	14:50:00	2024-09-26	12	323
1510	13:10:00	14:50:00	2024-10-03	12	323
1511	13:10:00	14:50:00	2024-10-10	12	323
1512	13:10:00	14:50:00	2024-10-17	12	323
1513	13:10:00	14:50:00	2024-10-24	12	323
1514	13:10:00	14:50:00	2024-10-31	12	323
1515	13:10:00	14:50:00	2024-11-07	12	323
1516	13:10:00	14:50:00	2024-11-14	12	323
1517	13:10:00	14:50:00	2024-11-21	12	323
1518	13:10:00	14:50:00	2024-11-28	12	323
1519	13:10:00	14:50:00	2024-12-05	12	323
1520	13:10:00	14:50:00	2024-12-12	12	323
1521	13:10:00	14:50:00	2024-08-06	13	324
1522	13:10:00	14:50:00	2024-08-13	13	324
1523	13:10:00	14:50:00	2024-08-20	13	324
1524	13:10:00	14:50:00	2024-08-27	13	324
1525	13:10:00	14:50:00	2024-09-03	13	324
1526	13:10:00	14:50:00	2024-09-10	13	324
1527	13:10:00	14:50:00	2024-09-17	13	324
1528	13:10:00	14:50:00	2024-09-24	13	324
1529	13:10:00	14:50:00	2024-10-01	13	324
1530	13:10:00	14:50:00	2024-10-08	13	324
1531	13:10:00	14:50:00	2024-10-15	13	324
1532	13:10:00	14:50:00	2024-10-22	13	324
1533	13:10:00	14:50:00	2024-10-29	13	324
1534	13:10:00	14:50:00	2024-11-05	13	324
1535	13:10:00	14:50:00	2024-11-12	13	324
1536	13:10:00	14:50:00	2024-11-19	13	324
1537	13:10:00	14:50:00	2024-11-26	13	324
1538	13:10:00	14:50:00	2024-12-03	13	324
1539	13:10:00	14:50:00	2024-12-10	13	324
1540	15:00:00	16:40:00	2024-08-08	13	325
1541	15:00:00	16:40:00	2024-08-15	13	325
1542	15:00:00	16:40:00	2024-08-22	13	325
1543	15:00:00	16:40:00	2024-08-29	13	325
1544	15:00:00	16:40:00	2024-09-05	13	325
1545	15:00:00	16:40:00	2024-09-12	13	325
1546	15:00:00	16:40:00	2024-09-19	13	325
1547	15:00:00	16:40:00	2024-09-26	13	325
1548	15:00:00	16:40:00	2024-10-03	13	325
1549	15:00:00	16:40:00	2024-10-10	13	325
1550	15:00:00	16:40:00	2024-10-17	13	325
1551	15:00:00	16:40:00	2024-10-24	13	325
1552	15:00:00	16:40:00	2024-10-31	13	325
1553	15:00:00	16:40:00	2024-11-07	13	325
1554	15:00:00	16:40:00	2024-11-14	13	325
1555	15:00:00	16:40:00	2024-11-21	13	325
1556	15:00:00	16:40:00	2024-11-28	13	325
1557	15:00:00	16:40:00	2024-12-05	13	325
1558	15:00:00	16:40:00	2024-12-12	13	325
1559	15:00:00	16:40:00	2024-08-06	7	326
1560	15:00:00	16:40:00	2024-08-13	7	326
1561	15:00:00	16:40:00	2024-08-20	7	326
1562	15:00:00	16:40:00	2024-08-27	7	326
1563	15:00:00	16:40:00	2024-09-03	7	326
1564	15:00:00	16:40:00	2024-09-10	7	326
1565	15:00:00	16:40:00	2024-09-17	7	326
1566	15:00:00	16:40:00	2024-09-24	7	326
1567	15:00:00	16:40:00	2024-10-01	7	326
1568	15:00:00	16:40:00	2024-10-08	7	326
1569	15:00:00	16:40:00	2024-10-15	7	326
1570	15:00:00	16:40:00	2024-10-22	7	326
1571	15:00:00	16:40:00	2024-10-29	7	326
1572	15:00:00	16:40:00	2024-11-05	7	326
1573	15:00:00	16:40:00	2024-11-12	7	326
1574	15:00:00	16:40:00	2024-11-19	7	326
1575	15:00:00	16:40:00	2024-11-26	7	326
1576	15:00:00	16:40:00	2024-12-03	7	326
1577	15:00:00	16:40:00	2024-12-10	7	326
1578	13:10:00	14:50:00	2024-08-08	7	327
1579	13:10:00	14:50:00	2024-08-15	7	327
1580	13:10:00	14:50:00	2024-08-22	7	327
1581	13:10:00	14:50:00	2024-08-29	7	327
1582	13:10:00	14:50:00	2024-09-05	7	327
1583	13:10:00	14:50:00	2024-09-12	7	327
1584	13:10:00	14:50:00	2024-09-19	7	327
1585	13:10:00	14:50:00	2024-09-26	7	327
1586	13:10:00	14:50:00	2024-10-03	7	327
1587	13:10:00	14:50:00	2024-10-10	7	327
1588	13:10:00	14:50:00	2024-10-17	7	327
1589	13:10:00	14:50:00	2024-10-24	7	327
1590	13:10:00	14:50:00	2024-10-31	7	327
1591	13:10:00	14:50:00	2024-11-07	7	327
1592	13:10:00	14:50:00	2024-11-14	7	327
1593	13:10:00	14:50:00	2024-11-21	7	327
1594	13:10:00	14:50:00	2024-11-28	7	327
1595	13:10:00	14:50:00	2024-12-05	7	327
1596	13:10:00	14:50:00	2024-12-12	7	327
1597	13:10:00	14:50:00	2024-08-06	69	328
1598	13:10:00	14:50:00	2024-08-13	69	328
1599	13:10:00	14:50:00	2024-08-20	69	328
1600	13:10:00	14:50:00	2024-08-27	69	328
1601	13:10:00	14:50:00	2024-09-03	69	328
1602	13:10:00	14:50:00	2024-09-10	69	328
1603	13:10:00	14:50:00	2024-09-17	69	328
1604	13:10:00	14:50:00	2024-09-24	69	328
1605	13:10:00	14:50:00	2024-10-01	69	328
1606	13:10:00	14:50:00	2024-10-08	69	328
1607	13:10:00	14:50:00	2024-10-15	69	328
1608	13:10:00	14:50:00	2024-10-22	69	328
1609	13:10:00	14:50:00	2024-10-29	69	328
1610	13:10:00	14:50:00	2024-11-05	69	328
1611	13:10:00	14:50:00	2024-11-12	69	328
1612	13:10:00	14:50:00	2024-11-19	69	328
1613	13:10:00	14:50:00	2024-11-26	69	328
1614	13:10:00	14:50:00	2024-12-03	69	328
1615	13:10:00	14:50:00	2024-12-10	69	328
1616	15:00:00	16:40:00	2024-08-08	69	329
1617	15:00:00	16:40:00	2024-08-15	69	329
1618	15:00:00	16:40:00	2024-08-22	69	329
1619	15:00:00	16:40:00	2024-08-29	69	329
1620	15:00:00	16:40:00	2024-09-05	69	329
1621	15:00:00	16:40:00	2024-09-12	69	329
1622	15:00:00	16:40:00	2024-09-19	69	329
1623	15:00:00	16:40:00	2024-09-26	69	329
1624	15:00:00	16:40:00	2024-10-03	69	329
1625	15:00:00	16:40:00	2024-10-10	69	329
1626	15:00:00	16:40:00	2024-10-17	69	329
1627	15:00:00	16:40:00	2024-10-24	69	329
1628	15:00:00	16:40:00	2024-10-31	69	329
1629	15:00:00	16:40:00	2024-11-07	69	329
1630	15:00:00	16:40:00	2024-11-14	69	329
1631	15:00:00	16:40:00	2024-11-21	69	329
1632	15:00:00	16:40:00	2024-11-28	69	329
1633	15:00:00	16:40:00	2024-12-05	69	329
1634	15:00:00	16:40:00	2024-12-12	69	329
1635	15:00:00	16:40:00	2024-08-06	20	330
1636	15:00:00	16:40:00	2024-08-13	20	330
1637	15:00:00	16:40:00	2024-08-20	20	330
1638	15:00:00	16:40:00	2024-08-27	20	330
1639	15:00:00	16:40:00	2024-09-03	20	330
1640	15:00:00	16:40:00	2024-09-10	20	330
1641	15:00:00	16:40:00	2024-09-17	20	330
1642	15:00:00	16:40:00	2024-09-24	20	330
1643	15:00:00	16:40:00	2024-10-01	20	330
1644	15:00:00	16:40:00	2024-10-08	20	330
1645	15:00:00	16:40:00	2024-10-15	20	330
1646	15:00:00	16:40:00	2024-10-22	20	330
1647	15:00:00	16:40:00	2024-10-29	20	330
1648	15:00:00	16:40:00	2024-11-05	20	330
1649	15:00:00	16:40:00	2024-11-12	20	330
1650	15:00:00	16:40:00	2024-11-19	20	330
1651	15:00:00	16:40:00	2024-11-26	20	330
1652	15:00:00	16:40:00	2024-12-03	20	330
1653	15:00:00	16:40:00	2024-12-10	20	330
1654	13:10:00	14:50:00	2024-08-08	20	331
1655	13:10:00	14:50:00	2024-08-15	20	331
1656	13:10:00	14:50:00	2024-08-22	20	331
1657	13:10:00	14:50:00	2024-08-29	20	331
1658	13:10:00	14:50:00	2024-09-05	20	331
1659	13:10:00	14:50:00	2024-09-12	20	331
1660	13:10:00	14:50:00	2024-09-19	20	331
1661	13:10:00	14:50:00	2024-09-26	20	331
1662	13:10:00	14:50:00	2024-10-03	20	331
1663	13:10:00	14:50:00	2024-10-10	20	331
1664	13:10:00	14:50:00	2024-10-17	20	331
1665	13:10:00	14:50:00	2024-10-24	20	331
1666	13:10:00	14:50:00	2024-10-31	20	331
1667	13:10:00	14:50:00	2024-11-07	20	331
1668	13:10:00	14:50:00	2024-11-14	20	331
1669	13:10:00	14:50:00	2024-11-21	20	331
1670	13:10:00	14:50:00	2024-11-28	20	331
1671	13:10:00	14:50:00	2024-12-05	20	331
1672	13:10:00	14:50:00	2024-12-12	20	331
1673	13:10:00	14:50:00	2024-08-06	9	332
1674	13:10:00	14:50:00	2024-08-13	9	332
1675	13:10:00	14:50:00	2024-08-20	9	332
1676	13:10:00	14:50:00	2024-08-27	9	332
1677	13:10:00	14:50:00	2024-09-03	9	332
1678	13:10:00	14:50:00	2024-09-10	9	332
1679	13:10:00	14:50:00	2024-09-17	9	332
1680	13:10:00	14:50:00	2024-09-24	9	332
1681	13:10:00	14:50:00	2024-10-01	9	332
1682	13:10:00	14:50:00	2024-10-08	9	332
1683	13:10:00	14:50:00	2024-10-15	9	332
1684	13:10:00	14:50:00	2024-10-22	9	332
1685	13:10:00	14:50:00	2024-10-29	9	332
1686	13:10:00	14:50:00	2024-11-05	9	332
1687	13:10:00	14:50:00	2024-11-12	9	332
1688	13:10:00	14:50:00	2024-11-19	9	332
1689	13:10:00	14:50:00	2024-11-26	9	332
1690	13:10:00	14:50:00	2024-12-03	9	332
1691	13:10:00	14:50:00	2024-12-10	9	332
1692	15:00:00	16:40:00	2024-08-08	9	333
1693	15:00:00	16:40:00	2024-08-15	9	333
1694	15:00:00	16:40:00	2024-08-22	9	333
1695	15:00:00	16:40:00	2024-08-29	9	333
1696	15:00:00	16:40:00	2024-09-05	9	333
1697	15:00:00	16:40:00	2024-09-12	9	333
1698	15:00:00	16:40:00	2024-09-19	9	333
1699	15:00:00	16:40:00	2024-09-26	9	333
1700	15:00:00	16:40:00	2024-10-03	9	333
1701	15:00:00	16:40:00	2024-10-10	9	333
1702	15:00:00	16:40:00	2024-10-17	9	333
1703	15:00:00	16:40:00	2024-10-24	9	333
1704	15:00:00	16:40:00	2024-10-31	9	333
1705	15:00:00	16:40:00	2024-11-07	9	333
1706	15:00:00	16:40:00	2024-11-14	9	333
1707	15:00:00	16:40:00	2024-11-21	9	333
1708	15:00:00	16:40:00	2024-11-28	9	333
1709	15:00:00	16:40:00	2024-12-05	9	333
1710	15:00:00	16:40:00	2024-12-12	9	333
1711	15:00:00	16:40:00	2024-08-06	3	334
1712	15:00:00	16:40:00	2024-08-13	3	334
1713	15:00:00	16:40:00	2024-08-20	3	334
1714	15:00:00	16:40:00	2024-08-27	3	334
1715	15:00:00	16:40:00	2024-09-03	3	334
1716	15:00:00	16:40:00	2024-09-10	3	334
1717	15:00:00	16:40:00	2024-09-17	3	334
1718	15:00:00	16:40:00	2024-09-24	3	334
1719	15:00:00	16:40:00	2024-10-01	3	334
1720	15:00:00	16:40:00	2024-10-08	3	334
1721	15:00:00	16:40:00	2024-10-15	3	334
1722	15:00:00	16:40:00	2024-10-22	3	334
1723	15:00:00	16:40:00	2024-10-29	3	334
1724	15:00:00	16:40:00	2024-11-05	3	334
1725	15:00:00	16:40:00	2024-11-12	3	334
1726	15:00:00	16:40:00	2024-11-19	3	334
1727	15:00:00	16:40:00	2024-11-26	3	334
1728	15:00:00	16:40:00	2024-12-03	3	334
1729	15:00:00	16:40:00	2024-12-10	3	334
1730	13:10:00	14:50:00	2024-08-08	3	335
1731	13:10:00	14:50:00	2024-08-15	3	335
1732	13:10:00	14:50:00	2024-08-22	3	335
1733	13:10:00	14:50:00	2024-08-29	3	335
1734	13:10:00	14:50:00	2024-09-05	3	335
1735	13:10:00	14:50:00	2024-09-12	3	335
1736	13:10:00	14:50:00	2024-09-19	3	335
1737	13:10:00	14:50:00	2024-09-26	3	335
1738	13:10:00	14:50:00	2024-10-03	3	335
1739	13:10:00	14:50:00	2024-10-10	3	335
1740	13:10:00	14:50:00	2024-10-17	3	335
1741	13:10:00	14:50:00	2024-10-24	3	335
1742	13:10:00	14:50:00	2024-10-31	3	335
1743	13:10:00	14:50:00	2024-11-07	3	335
1744	13:10:00	14:50:00	2024-11-14	3	335
1745	13:10:00	14:50:00	2024-11-21	3	335
1746	13:10:00	14:50:00	2024-11-28	3	335
1747	13:10:00	14:50:00	2024-12-05	3	335
1748	13:10:00	14:50:00	2024-12-12	3	335
1749	15:00:00	16:40:00	2024-08-06	8	336
1750	15:00:00	16:40:00	2024-08-13	8	336
1751	15:00:00	16:40:00	2024-08-20	8	336
1752	15:00:00	16:40:00	2024-08-27	8	336
1753	15:00:00	16:40:00	2024-09-03	8	336
1754	15:00:00	16:40:00	2024-09-10	8	336
1755	15:00:00	16:40:00	2024-09-17	8	336
1756	15:00:00	16:40:00	2024-09-24	8	336
1757	15:00:00	16:40:00	2024-10-01	8	336
1758	15:00:00	16:40:00	2024-10-08	8	336
1759	15:00:00	16:40:00	2024-10-15	8	336
1760	15:00:00	16:40:00	2024-10-22	8	336
1761	15:00:00	16:40:00	2024-10-29	8	336
1762	15:00:00	16:40:00	2024-11-05	8	336
1763	15:00:00	16:40:00	2024-11-12	8	336
1764	15:00:00	16:40:00	2024-11-19	8	336
1765	15:00:00	16:40:00	2024-11-26	8	336
1766	15:00:00	16:40:00	2024-12-03	8	336
1767	15:00:00	16:40:00	2024-12-10	8	336
1768	13:10:00	14:50:00	2024-08-08	8	337
1769	13:10:00	14:50:00	2024-08-15	8	337
1770	13:10:00	14:50:00	2024-08-22	8	337
1771	13:10:00	14:50:00	2024-08-29	8	337
1772	13:10:00	14:50:00	2024-09-05	8	337
1773	13:10:00	14:50:00	2024-09-12	8	337
1774	13:10:00	14:50:00	2024-09-19	8	337
1775	13:10:00	14:50:00	2024-09-26	8	337
1776	13:10:00	14:50:00	2024-10-03	8	337
1777	13:10:00	14:50:00	2024-10-10	8	337
1778	13:10:00	14:50:00	2024-10-17	8	337
1779	13:10:00	14:50:00	2024-10-24	8	337
1780	13:10:00	14:50:00	2024-10-31	8	337
1781	13:10:00	14:50:00	2024-11-07	8	337
1782	13:10:00	14:50:00	2024-11-14	8	337
1783	13:10:00	14:50:00	2024-11-21	8	337
1784	13:10:00	14:50:00	2024-11-28	8	337
1785	13:10:00	14:50:00	2024-12-05	8	337
1786	13:10:00	14:50:00	2024-12-12	8	337
1787	11:10:00	12:50:00	2024-08-05	16	338
1788	11:10:00	12:50:00	2024-08-12	16	338
1789	11:10:00	12:50:00	2024-08-19	16	338
1790	11:10:00	12:50:00	2024-08-26	16	338
1791	11:10:00	12:50:00	2024-09-02	16	338
1792	11:10:00	12:50:00	2024-09-09	16	338
1793	11:10:00	12:50:00	2024-09-16	16	338
1794	11:10:00	12:50:00	2024-09-23	16	338
1795	11:10:00	12:50:00	2024-09-30	16	338
1796	11:10:00	12:50:00	2024-10-07	16	338
1797	11:10:00	12:50:00	2024-10-14	16	338
1798	11:10:00	12:50:00	2024-10-21	16	338
1799	11:10:00	12:50:00	2024-10-28	16	338
1800	11:10:00	12:50:00	2024-11-04	16	338
1801	11:10:00	12:50:00	2024-11-11	16	338
1802	11:10:00	12:50:00	2024-11-18	16	338
1803	11:10:00	12:50:00	2024-11-25	16	338
1804	11:10:00	12:50:00	2024-12-02	16	338
1805	11:10:00	12:50:00	2024-12-09	16	338
4520	09:20:00	11:00:00	2024-11-14	31	59
4521	09:20:00	11:00:00	2024-11-21	31	59
4522	09:20:00	11:00:00	2024-11-28	31	59
4523	09:20:00	11:00:00	2024-12-05	31	59
4524	09:20:00	11:00:00	2024-12-12	31	59
4563	07:30:00	09:10:00	2024-08-06	30	62
4564	07:30:00	09:10:00	2024-08-13	30	62
4565	07:30:00	09:10:00	2024-08-20	30	62
4566	07:30:00	09:10:00	2024-08-27	30	62
4567	07:30:00	09:10:00	2024-09-03	30	62
4568	07:30:00	09:10:00	2024-09-10	30	62
4569	07:30:00	09:10:00	2024-09-17	30	62
4570	07:30:00	09:10:00	2024-09-24	30	62
4571	07:30:00	09:10:00	2024-10-01	30	62
4572	07:30:00	09:10:00	2024-10-08	30	62
4573	07:30:00	09:10:00	2024-10-15	30	62
4574	07:30:00	09:10:00	2024-10-22	30	62
4575	07:30:00	09:10:00	2024-10-29	30	62
4576	07:30:00	09:10:00	2024-11-05	30	62
4577	07:30:00	09:10:00	2024-11-12	30	62
4578	07:30:00	09:10:00	2024-11-19	30	62
4579	07:30:00	09:10:00	2024-11-26	30	62
4580	07:30:00	09:10:00	2024-12-03	30	62
4581	07:30:00	09:10:00	2024-12-10	30	62
4582	07:30:00	09:10:00	2024-08-09	38	63
4583	07:30:00	09:10:00	2024-08-16	38	63
4584	07:30:00	09:10:00	2024-08-23	38	63
4585	07:30:00	09:10:00	2024-08-30	38	63
4586	07:30:00	09:10:00	2024-09-06	38	63
4587	07:30:00	09:10:00	2024-09-13	38	63
4588	07:30:00	09:10:00	2024-09-20	38	63
4589	07:30:00	09:10:00	2024-09-27	38	63
4590	07:30:00	09:10:00	2024-10-04	38	63
4591	07:30:00	09:10:00	2024-10-11	38	63
4592	07:30:00	09:10:00	2024-10-18	38	63
4593	07:30:00	09:10:00	2024-10-25	38	63
4594	07:30:00	09:10:00	2024-11-01	38	63
4595	07:30:00	09:10:00	2024-11-08	38	63
4596	07:30:00	09:10:00	2024-11-15	38	63
4597	07:30:00	09:10:00	2024-11-22	38	63
4598	07:30:00	09:10:00	2024-11-29	38	63
4599	07:30:00	09:10:00	2024-12-06	38	63
5597	13:10:00	14:50:00	2024-11-06	33	134
5598	13:10:00	14:50:00	2024-11-13	33	134
5599	13:10:00	14:50:00	2024-11-20	33	134
5600	13:10:00	14:50:00	2024-11-27	33	134
4623	07:30:00	09:10:00	2024-09-06	31	65
4624	07:30:00	09:10:00	2024-09-13	31	65
4625	07:30:00	09:10:00	2024-09-20	31	65
4626	07:30:00	09:10:00	2024-09-27	31	65
4627	07:30:00	09:10:00	2024-10-04	31	65
4628	07:30:00	09:10:00	2024-10-11	31	65
4629	07:30:00	09:10:00	2024-10-18	31	65
4630	07:30:00	09:10:00	2024-10-25	31	65
4631	07:30:00	09:10:00	2024-11-01	31	65
4632	07:30:00	09:10:00	2024-11-08	31	65
4633	07:30:00	09:10:00	2024-11-15	31	65
4634	07:30:00	09:10:00	2024-11-22	31	65
4635	07:30:00	09:10:00	2024-11-29	31	65
4636	07:30:00	09:10:00	2024-12-06	31	65
5601	13:10:00	14:50:00	2024-12-04	33	134
5602	13:10:00	14:50:00	2024-12-11	33	134
5641	15:00:00	16:40:00	2024-08-05	24	137
5642	15:00:00	16:40:00	2024-08-12	24	137
5643	15:00:00	16:40:00	2024-08-19	24	137
5644	15:00:00	16:40:00	2024-08-26	24	137
5645	15:00:00	16:40:00	2024-09-02	24	137
5646	15:00:00	16:40:00	2024-09-09	24	137
5647	15:00:00	16:40:00	2024-09-16	24	137
5648	15:00:00	16:40:00	2024-09-23	24	137
5649	15:00:00	16:40:00	2024-09-30	24	137
5650	15:00:00	16:40:00	2024-10-07	24	137
5651	15:00:00	16:40:00	2024-10-14	24	137
5652	15:00:00	16:40:00	2024-10-21	24	137
5653	15:00:00	16:40:00	2024-10-28	24	137
5654	15:00:00	16:40:00	2024-11-04	24	137
5655	15:00:00	16:40:00	2024-11-11	24	137
5656	15:00:00	16:40:00	2024-11-18	24	137
5657	15:00:00	16:40:00	2024-11-25	24	137
5658	15:00:00	16:40:00	2024-12-02	24	137
5659	15:00:00	16:40:00	2024-12-09	24	137
5660	13:10:00	14:50:00	2024-08-07	24	138
5661	13:10:00	14:50:00	2024-08-14	24	138
5662	13:10:00	14:50:00	2024-08-21	24	138
5663	13:10:00	14:50:00	2024-08-28	24	138
5664	13:10:00	14:50:00	2024-09-04	24	138
5665	13:10:00	14:50:00	2024-09-11	24	138
5666	13:10:00	14:50:00	2024-09-18	24	138
5667	13:10:00	14:50:00	2024-09-25	24	138
5668	13:10:00	14:50:00	2024-10-02	24	138
5669	13:10:00	14:50:00	2024-10-09	24	138
5670	13:10:00	14:50:00	2024-10-16	24	138
5671	13:10:00	14:50:00	2024-10-23	24	138
5672	13:10:00	14:50:00	2024-10-30	24	138
5673	13:10:00	14:50:00	2024-11-06	24	138
5674	13:10:00	14:50:00	2024-11-13	24	138
5675	13:10:00	14:50:00	2024-11-20	24	138
5676	13:10:00	14:50:00	2024-11-27	24	138
5677	13:10:00	14:50:00	2024-12-04	24	138
5678	13:10:00	14:50:00	2024-12-11	24	138
5773	09:20:00	11:00:00	2024-08-07	38	145
5774	09:20:00	11:00:00	2024-08-14	38	145
5775	09:20:00	11:00:00	2024-08-21	38	145
5776	09:20:00	11:00:00	2024-08-28	38	145
5777	09:20:00	11:00:00	2024-09-04	38	145
5778	09:20:00	11:00:00	2024-09-11	38	145
5779	09:20:00	11:00:00	2024-09-18	38	145
5780	09:20:00	11:00:00	2024-09-25	38	145
5781	09:20:00	11:00:00	2024-10-02	38	145
5782	09:20:00	11:00:00	2024-10-09	38	145
5783	09:20:00	11:00:00	2024-10-16	38	145
5784	09:20:00	11:00:00	2024-10-23	38	145
5785	09:20:00	11:00:00	2024-10-30	38	145
5786	09:20:00	11:00:00	2024-11-06	38	145
5787	09:20:00	11:00:00	2024-11-13	38	145
5788	09:20:00	11:00:00	2024-11-20	38	145
5789	09:20:00	11:00:00	2024-11-27	38	145
5790	09:20:00	11:00:00	2024-12-04	38	145
5791	09:20:00	11:00:00	2024-12-11	38	145
5792	11:10:00	12:50:00	2024-08-09	33	146
5793	11:10:00	12:50:00	2024-08-16	33	146
5794	11:10:00	12:50:00	2024-08-23	33	146
5795	11:10:00	12:50:00	2024-08-30	33	146
5796	11:10:00	12:50:00	2024-09-06	33	146
5797	11:10:00	12:50:00	2024-09-13	33	146
5798	11:10:00	12:50:00	2024-09-20	33	146
5799	11:10:00	12:50:00	2024-09-27	33	146
5800	11:10:00	12:50:00	2024-10-04	33	146
5801	11:10:00	12:50:00	2024-10-11	33	146
5802	11:10:00	12:50:00	2024-10-18	33	146
5803	11:10:00	12:50:00	2024-10-25	33	146
5804	11:10:00	12:50:00	2024-11-01	33	146
5805	11:10:00	12:50:00	2024-11-08	33	146
5806	11:10:00	12:50:00	2024-11-15	33	146
5807	11:10:00	12:50:00	2024-11-22	33	146
5808	11:10:00	12:50:00	2024-11-29	33	146
5809	11:10:00	12:50:00	2024-12-06	33	146
5944	09:20:00	12:50:00	2024-08-22	24	155
5945	09:20:00	12:50:00	2024-08-29	24	155
5946	09:20:00	12:50:00	2024-09-05	24	155
5947	09:20:00	12:50:00	2024-09-12	24	155
5948	09:20:00	12:50:00	2024-09-19	24	155
5949	09:20:00	12:50:00	2024-09-26	24	155
5950	09:20:00	12:50:00	2024-10-03	24	155
5951	09:20:00	12:50:00	2024-10-10	24	155
5952	09:20:00	12:50:00	2024-10-17	24	155
5953	09:20:00	12:50:00	2024-10-24	24	155
5954	09:20:00	12:50:00	2024-10-31	24	155
5955	09:20:00	12:50:00	2024-11-07	24	155
5956	09:20:00	12:50:00	2024-11-14	24	155
5957	09:20:00	12:50:00	2024-11-21	24	155
5958	09:20:00	12:50:00	2024-11-28	24	155
5959	09:20:00	12:50:00	2024-12-05	24	155
5960	09:20:00	12:50:00	2024-12-12	24	155
5961	09:20:00	12:50:00	2024-08-08	39	153
5962	09:20:00	12:50:00	2024-08-15	39	153
5963	09:20:00	12:50:00	2024-08-22	39	153
5964	09:20:00	12:50:00	2024-08-29	39	153
5965	09:20:00	12:50:00	2024-09-05	39	153
5966	09:20:00	12:50:00	2024-09-12	39	153
5967	09:20:00	12:50:00	2024-09-19	39	153
5968	09:20:00	12:50:00	2024-09-26	39	153
5969	09:20:00	12:50:00	2024-10-03	39	153
5970	09:20:00	12:50:00	2024-10-10	39	153
5971	09:20:00	12:50:00	2024-10-17	39	153
5972	09:20:00	12:50:00	2024-10-24	39	153
4637	07:30:00	09:10:00	2024-08-06	33	66
4638	07:30:00	09:10:00	2024-08-13	33	66
4639	07:30:00	09:10:00	2024-08-20	33	66
4640	07:30:00	09:10:00	2024-08-27	33	66
4641	07:30:00	09:10:00	2024-09-03	33	66
4642	07:30:00	09:10:00	2024-09-10	33	66
4643	07:30:00	09:10:00	2024-09-17	33	66
4644	07:30:00	09:10:00	2024-09-24	33	66
4645	07:30:00	09:10:00	2024-10-01	33	66
4646	07:30:00	09:10:00	2024-10-08	33	66
4647	07:30:00	09:10:00	2024-10-15	33	66
4648	07:30:00	09:10:00	2024-10-22	33	66
4649	07:30:00	09:10:00	2024-10-29	33	66
4650	07:30:00	09:10:00	2024-11-05	33	66
4651	07:30:00	09:10:00	2024-11-12	33	66
4652	07:30:00	09:10:00	2024-11-19	33	66
4653	07:30:00	09:10:00	2024-11-26	33	66
4654	07:30:00	09:10:00	2024-12-03	33	66
4655	07:30:00	09:10:00	2024-12-10	33	66
4656	07:30:00	09:10:00	2024-08-09	33	67
4657	07:30:00	09:10:00	2024-08-16	33	67
4658	07:30:00	09:10:00	2024-08-23	33	67
4659	07:30:00	09:10:00	2024-08-30	33	67
4660	07:30:00	09:10:00	2024-09-06	33	67
4661	07:30:00	09:10:00	2024-09-13	33	67
4662	07:30:00	09:10:00	2024-09-20	33	67
4663	07:30:00	09:10:00	2024-09-27	33	67
4664	07:30:00	09:10:00	2024-10-04	33	67
4665	07:30:00	09:10:00	2024-10-11	33	67
4666	07:30:00	09:10:00	2024-10-18	33	67
4667	07:30:00	09:10:00	2024-10-25	33	67
4668	07:30:00	09:10:00	2024-11-01	33	67
4669	07:30:00	09:10:00	2024-11-08	33	67
4670	07:30:00	09:10:00	2024-11-15	33	67
1906	15:00:00	16:40:00	2024-08-06	2	345
1907	15:00:00	16:40:00	2024-08-13	2	345
1908	15:00:00	16:40:00	2024-08-20	2	345
1909	15:00:00	16:40:00	2024-08-27	2	345
1910	15:00:00	16:40:00	2024-09-03	2	345
1911	15:00:00	16:40:00	2024-09-10	2	345
1912	15:00:00	16:40:00	2024-09-17	2	345
1913	15:00:00	16:40:00	2024-09-24	2	345
1914	15:00:00	16:40:00	2024-10-01	2	345
1915	15:00:00	16:40:00	2024-10-08	2	345
1916	15:00:00	16:40:00	2024-10-15	2	345
1917	15:00:00	16:40:00	2024-10-22	2	345
1918	15:00:00	16:40:00	2024-10-29	2	345
1919	15:00:00	16:40:00	2024-11-05	2	345
1920	15:00:00	16:40:00	2024-11-12	2	345
1921	15:00:00	16:40:00	2024-11-19	2	345
1922	15:00:00	16:40:00	2024-11-26	2	345
1923	15:00:00	16:40:00	2024-12-03	2	345
1924	15:00:00	16:40:00	2024-12-10	2	345
1925	13:10:00	14:50:00	2024-08-08	2	346
1926	13:10:00	14:50:00	2024-08-15	2	346
1927	13:10:00	14:50:00	2024-08-22	2	346
1928	13:10:00	14:50:00	2024-08-29	2	346
1929	13:10:00	14:50:00	2024-09-05	2	346
1930	13:10:00	14:50:00	2024-09-12	2	346
1931	13:10:00	14:50:00	2024-09-19	2	346
1932	13:10:00	14:50:00	2024-09-26	2	346
1933	13:10:00	14:50:00	2024-10-03	2	346
1934	13:10:00	14:50:00	2024-10-10	2	346
1935	13:10:00	14:50:00	2024-10-17	2	346
1936	13:10:00	14:50:00	2024-10-24	2	346
1937	13:10:00	14:50:00	2024-10-31	2	346
1938	13:10:00	14:50:00	2024-11-07	2	346
1939	13:10:00	14:50:00	2024-11-14	2	346
1940	13:10:00	14:50:00	2024-11-21	2	346
1941	13:10:00	14:50:00	2024-11-28	2	346
1942	13:10:00	14:50:00	2024-12-05	2	346
1943	13:10:00	14:50:00	2024-12-12	2	346
4671	07:30:00	09:10:00	2024-11-22	33	67
4672	07:30:00	09:10:00	2024-11-29	33	67
4673	07:30:00	09:10:00	2024-12-06	33	67
5634	13:10:00	14:50:00	2024-10-30	31	136
5635	13:10:00	14:50:00	2024-11-06	31	136
5636	13:10:00	14:50:00	2024-11-13	31	136
5637	13:10:00	14:50:00	2024-11-20	31	136
5638	13:10:00	14:50:00	2024-11-27	31	136
5639	13:10:00	14:50:00	2024-12-04	31	136
5640	13:10:00	14:50:00	2024-12-11	31	136
5863	07:30:00	09:10:00	2024-11-21	26	149
5864	07:30:00	09:10:00	2024-11-28	26	149
5865	07:30:00	09:10:00	2024-12-05	26	149
5866	07:30:00	09:10:00	2024-12-12	26	149
5973	09:20:00	12:50:00	2024-10-31	39	153
5974	09:20:00	12:50:00	2024-11-07	39	153
5975	09:20:00	12:50:00	2024-11-14	39	153
5976	09:20:00	12:50:00	2024-11-21	39	153
5977	09:20:00	12:50:00	2024-11-28	39	153
5978	09:20:00	12:50:00	2024-12-05	39	153
5979	09:20:00	12:50:00	2024-12-12	39	153
5980	09:20:00	11:00:00	2024-08-05	26	156
5981	09:20:00	11:00:00	2024-08-12	26	156
5982	09:20:00	11:00:00	2024-08-19	26	156
5983	09:20:00	11:00:00	2024-08-26	26	156
5984	09:20:00	11:00:00	2024-09-02	26	156
5985	09:20:00	11:00:00	2024-09-09	26	156
5986	09:20:00	11:00:00	2024-09-16	26	156
5987	09:20:00	11:00:00	2024-09-23	26	156
5988	09:20:00	11:00:00	2024-09-30	26	156
5989	09:20:00	11:00:00	2024-10-07	26	156
5990	09:20:00	11:00:00	2024-10-14	26	156
5991	09:20:00	11:00:00	2024-10-21	26	156
5992	09:20:00	11:00:00	2024-10-28	26	156
5993	09:20:00	11:00:00	2024-11-04	26	156
5994	09:20:00	11:00:00	2024-11-11	26	156
5995	09:20:00	11:00:00	2024-11-18	26	156
5996	09:20:00	11:00:00	2024-11-25	26	156
5997	09:20:00	11:00:00	2024-12-02	26	156
5998	09:20:00	11:00:00	2024-12-09	26	156
5999	07:30:00	09:10:00	2024-08-06	65	157
6000	07:30:00	09:10:00	2024-08-13	65	157
6001	07:30:00	09:10:00	2024-08-20	65	157
6002	07:30:00	09:10:00	2024-08-27	65	157
6003	07:30:00	09:10:00	2024-09-03	65	157
6004	07:30:00	09:10:00	2024-09-10	65	157
6005	07:30:00	09:10:00	2024-09-17	65	157
6006	07:30:00	09:10:00	2024-09-24	65	157
1944	13:10:00	14:50:00	2024-08-06	2	347
1945	13:10:00	14:50:00	2024-08-13	2	347
1946	13:10:00	14:50:00	2024-08-20	2	347
1947	13:10:00	14:50:00	2024-08-27	2	347
1948	13:10:00	14:50:00	2024-09-03	2	347
1949	13:10:00	14:50:00	2024-09-10	2	347
1950	13:10:00	14:50:00	2024-09-17	2	347
1951	13:10:00	14:50:00	2024-09-24	2	347
1952	13:10:00	14:50:00	2024-10-01	2	347
1953	13:10:00	14:50:00	2024-10-08	2	347
1954	13:10:00	14:50:00	2024-10-15	2	347
1955	13:10:00	14:50:00	2024-10-22	2	347
1956	13:10:00	14:50:00	2024-10-29	2	347
1957	13:10:00	14:50:00	2024-11-05	2	347
1958	13:10:00	14:50:00	2024-11-12	2	347
1959	13:10:00	14:50:00	2024-11-19	2	347
1960	13:10:00	14:50:00	2024-11-26	2	347
1961	13:10:00	14:50:00	2024-12-03	2	347
1962	13:10:00	14:50:00	2024-12-10	2	347
1963	15:00:00	16:40:00	2024-08-08	2	348
1964	15:00:00	16:40:00	2024-08-15	2	348
1965	15:00:00	16:40:00	2024-08-22	2	348
1966	15:00:00	16:40:00	2024-08-29	2	348
1967	15:00:00	16:40:00	2024-09-05	2	348
1968	15:00:00	16:40:00	2024-09-12	2	348
1969	15:00:00	16:40:00	2024-09-19	2	348
1970	15:00:00	16:40:00	2024-09-26	2	348
1971	15:00:00	16:40:00	2024-10-03	2	348
1972	15:00:00	16:40:00	2024-10-10	2	348
1973	15:00:00	16:40:00	2024-10-17	2	348
1974	15:00:00	16:40:00	2024-10-24	2	348
1975	15:00:00	16:40:00	2024-10-31	2	348
1976	15:00:00	16:40:00	2024-11-07	2	348
1977	15:00:00	16:40:00	2024-11-14	2	348
1978	15:00:00	16:40:00	2024-11-21	2	348
1979	15:00:00	16:40:00	2024-11-28	2	348
1980	15:00:00	16:40:00	2024-12-05	2	348
1981	15:00:00	16:40:00	2024-12-12	2	348
1982	15:00:00	16:40:00	2024-08-06	3	349
1983	15:00:00	16:40:00	2024-08-13	3	349
1984	15:00:00	16:40:00	2024-08-20	3	349
1985	15:00:00	16:40:00	2024-08-27	3	349
1986	15:00:00	16:40:00	2024-09-03	3	349
1987	15:00:00	16:40:00	2024-09-10	3	349
1988	15:00:00	16:40:00	2024-09-17	3	349
1989	15:00:00	16:40:00	2024-09-24	3	349
1990	15:00:00	16:40:00	2024-10-01	3	349
1991	15:00:00	16:40:00	2024-10-08	3	349
1992	15:00:00	16:40:00	2024-10-15	3	349
1993	15:00:00	16:40:00	2024-10-22	3	349
1994	15:00:00	16:40:00	2024-10-29	3	349
1995	15:00:00	16:40:00	2024-11-05	3	349
1996	15:00:00	16:40:00	2024-11-12	3	349
1997	15:00:00	16:40:00	2024-11-19	3	349
1998	15:00:00	16:40:00	2024-11-26	3	349
1999	15:00:00	16:40:00	2024-12-03	3	349
2000	15:00:00	16:40:00	2024-12-10	3	349
2001	13:10:00	14:50:00	2024-08-08	3	350
2002	13:10:00	14:50:00	2024-08-15	3	350
2003	13:10:00	14:50:00	2024-08-22	3	350
2004	13:10:00	14:50:00	2024-08-29	3	350
2005	13:10:00	14:50:00	2024-09-05	3	350
2006	13:10:00	14:50:00	2024-09-12	3	350
2007	13:10:00	14:50:00	2024-09-19	3	350
2008	13:10:00	14:50:00	2024-09-26	3	350
2009	13:10:00	14:50:00	2024-10-03	3	350
2010	13:10:00	14:50:00	2024-10-10	3	350
2011	13:10:00	14:50:00	2024-10-17	3	350
2012	13:10:00	14:50:00	2024-10-24	3	350
2013	13:10:00	14:50:00	2024-10-31	3	350
2014	13:10:00	14:50:00	2024-11-07	3	350
2015	13:10:00	14:50:00	2024-11-14	3	350
2016	13:10:00	14:50:00	2024-11-21	3	350
2017	13:10:00	14:50:00	2024-11-28	3	350
2018	13:10:00	14:50:00	2024-12-05	3	350
2019	13:10:00	14:50:00	2024-12-12	3	350
2020	13:10:00	14:50:00	2024-08-06	3	351
2021	13:10:00	14:50:00	2024-08-13	3	351
2022	13:10:00	14:50:00	2024-08-20	3	351
2023	13:10:00	14:50:00	2024-08-27	3	351
2024	13:10:00	14:50:00	2024-09-03	3	351
2025	13:10:00	14:50:00	2024-09-10	3	351
2026	13:10:00	14:50:00	2024-09-17	3	351
2027	13:10:00	14:50:00	2024-09-24	3	351
2028	13:10:00	14:50:00	2024-10-01	3	351
2029	13:10:00	14:50:00	2024-10-08	3	351
2030	13:10:00	14:50:00	2024-10-15	3	351
2031	13:10:00	14:50:00	2024-10-22	3	351
2032	13:10:00	14:50:00	2024-10-29	3	351
2033	13:10:00	14:50:00	2024-11-05	3	351
2034	13:10:00	14:50:00	2024-11-12	3	351
2035	13:10:00	14:50:00	2024-11-19	3	351
2036	13:10:00	14:50:00	2024-11-26	3	351
2037	13:10:00	14:50:00	2024-12-03	3	351
2038	13:10:00	14:50:00	2024-12-10	3	351
2039	15:00:00	16:40:00	2024-08-08	3	352
2040	15:00:00	16:40:00	2024-08-15	3	352
2041	15:00:00	16:40:00	2024-08-22	3	352
2042	15:00:00	16:40:00	2024-08-29	3	352
2043	15:00:00	16:40:00	2024-09-05	3	352
2044	15:00:00	16:40:00	2024-09-12	3	352
2045	15:00:00	16:40:00	2024-09-19	3	352
2046	15:00:00	16:40:00	2024-09-26	3	352
2047	15:00:00	16:40:00	2024-10-03	3	352
2048	15:00:00	16:40:00	2024-10-10	3	352
2049	15:00:00	16:40:00	2024-10-17	3	352
2050	15:00:00	16:40:00	2024-10-24	3	352
2051	15:00:00	16:40:00	2024-10-31	3	352
2052	15:00:00	16:40:00	2024-11-07	3	352
2053	15:00:00	16:40:00	2024-11-14	3	352
2054	15:00:00	16:40:00	2024-11-21	3	352
2055	15:00:00	16:40:00	2024-11-28	3	352
2056	15:00:00	16:40:00	2024-12-05	3	352
2057	15:00:00	16:40:00	2024-12-12	3	352
2058	15:00:00	16:40:00	2024-08-06	4	353
2059	15:00:00	16:40:00	2024-08-13	4	353
2060	15:00:00	16:40:00	2024-08-20	4	353
2061	15:00:00	16:40:00	2024-08-27	4	353
2062	15:00:00	16:40:00	2024-09-03	4	353
2063	15:00:00	16:40:00	2024-09-10	4	353
2064	15:00:00	16:40:00	2024-09-17	4	353
2065	15:00:00	16:40:00	2024-09-24	4	353
2066	15:00:00	16:40:00	2024-10-01	4	353
2067	15:00:00	16:40:00	2024-10-08	4	353
2068	15:00:00	16:40:00	2024-10-15	4	353
2069	15:00:00	16:40:00	2024-10-22	4	353
2070	15:00:00	16:40:00	2024-10-29	4	353
2071	15:00:00	16:40:00	2024-11-05	4	353
2072	15:00:00	16:40:00	2024-11-12	4	353
2073	15:00:00	16:40:00	2024-11-19	4	353
2074	15:00:00	16:40:00	2024-11-26	4	353
2075	15:00:00	16:40:00	2024-12-03	4	353
2076	15:00:00	16:40:00	2024-12-10	4	353
2077	13:10:00	14:50:00	2024-08-08	4	354
2078	13:10:00	14:50:00	2024-08-15	4	354
2079	13:10:00	14:50:00	2024-08-22	4	354
2080	13:10:00	14:50:00	2024-08-29	4	354
2081	13:10:00	14:50:00	2024-09-05	4	354
2082	13:10:00	14:50:00	2024-09-12	4	354
2083	13:10:00	14:50:00	2024-09-19	4	354
2084	13:10:00	14:50:00	2024-09-26	4	354
2085	13:10:00	14:50:00	2024-10-03	4	354
2086	13:10:00	14:50:00	2024-10-10	4	354
2087	13:10:00	14:50:00	2024-10-17	4	354
2088	13:10:00	14:50:00	2024-10-24	4	354
2089	13:10:00	14:50:00	2024-10-31	4	354
2090	13:10:00	14:50:00	2024-11-07	4	354
2091	13:10:00	14:50:00	2024-11-14	4	354
2092	13:10:00	14:50:00	2024-11-21	4	354
2093	13:10:00	14:50:00	2024-11-28	4	354
2094	13:10:00	14:50:00	2024-12-05	4	354
2095	13:10:00	14:50:00	2024-12-12	4	354
2134	15:00:00	16:40:00	2024-08-06	5	357
2135	15:00:00	16:40:00	2024-08-13	5	357
2136	15:00:00	16:40:00	2024-08-20	5	357
2137	15:00:00	16:40:00	2024-08-27	5	357
2138	15:00:00	16:40:00	2024-09-03	5	357
2139	15:00:00	16:40:00	2024-09-10	5	357
2140	15:00:00	16:40:00	2024-09-17	5	357
2141	15:00:00	16:40:00	2024-09-24	5	357
2142	15:00:00	16:40:00	2024-10-01	5	357
2143	15:00:00	16:40:00	2024-10-08	5	357
2144	15:00:00	16:40:00	2024-10-15	5	357
2145	15:00:00	16:40:00	2024-10-22	5	357
2146	15:00:00	16:40:00	2024-10-29	5	357
2147	15:00:00	16:40:00	2024-11-05	5	357
2148	15:00:00	16:40:00	2024-11-12	5	357
2149	15:00:00	16:40:00	2024-11-19	5	357
2150	15:00:00	16:40:00	2024-11-26	5	357
2151	15:00:00	16:40:00	2024-12-03	5	357
2152	15:00:00	16:40:00	2024-12-10	5	357
2153	13:10:00	14:50:00	2024-08-08	5	358
2154	13:10:00	14:50:00	2024-08-15	5	358
2155	13:10:00	14:50:00	2024-08-22	5	358
2156	13:10:00	14:50:00	2024-08-29	5	358
2157	13:10:00	14:50:00	2024-09-05	5	358
2158	13:10:00	14:50:00	2024-09-12	5	358
2159	13:10:00	14:50:00	2024-09-19	5	358
2160	13:10:00	14:50:00	2024-09-26	5	358
2161	13:10:00	14:50:00	2024-10-03	5	358
2162	13:10:00	14:50:00	2024-10-10	5	358
2163	13:10:00	14:50:00	2024-10-17	5	358
2164	13:10:00	14:50:00	2024-10-24	5	358
2165	13:10:00	14:50:00	2024-10-31	5	358
2166	13:10:00	14:50:00	2024-11-07	5	358
2167	13:10:00	14:50:00	2024-11-14	5	358
2168	13:10:00	14:50:00	2024-11-21	5	358
2169	13:10:00	14:50:00	2024-11-28	5	358
2170	13:10:00	14:50:00	2024-12-05	5	358
2171	13:10:00	14:50:00	2024-12-12	5	358
2210	13:10:00	14:50:00	2024-08-06	6	361
2211	13:10:00	14:50:00	2024-08-13	6	361
2212	13:10:00	14:50:00	2024-08-20	6	361
2213	13:10:00	14:50:00	2024-08-27	6	361
2214	13:10:00	14:50:00	2024-09-03	6	361
2215	13:10:00	14:50:00	2024-09-10	6	361
2216	13:10:00	14:50:00	2024-09-17	6	361
2217	13:10:00	14:50:00	2024-09-24	6	361
2218	13:10:00	14:50:00	2024-10-01	6	361
2219	13:10:00	14:50:00	2024-10-08	6	361
2220	13:10:00	14:50:00	2024-10-15	6	361
2221	13:10:00	14:50:00	2024-10-22	6	361
2222	13:10:00	14:50:00	2024-10-29	6	361
2223	13:10:00	14:50:00	2024-11-05	6	361
2224	13:10:00	14:50:00	2024-11-12	6	361
2225	13:10:00	14:50:00	2024-11-19	6	361
2226	13:10:00	14:50:00	2024-11-26	6	361
2227	13:10:00	14:50:00	2024-12-03	6	361
2228	13:10:00	14:50:00	2024-12-10	6	361
2229	15:00:00	16:40:00	2024-08-08	6	362
2230	15:00:00	16:40:00	2024-08-15	6	362
2231	15:00:00	16:40:00	2024-08-22	6	362
2232	15:00:00	16:40:00	2024-08-29	6	362
2233	15:00:00	16:40:00	2024-09-05	6	362
2234	15:00:00	16:40:00	2024-09-12	6	362
2235	15:00:00	16:40:00	2024-09-19	6	362
2236	15:00:00	16:40:00	2024-09-26	6	362
2237	15:00:00	16:40:00	2024-10-03	6	362
2238	15:00:00	16:40:00	2024-10-10	6	362
2239	15:00:00	16:40:00	2024-10-17	6	362
2240	15:00:00	16:40:00	2024-10-24	6	362
2241	15:00:00	16:40:00	2024-10-31	6	362
2242	15:00:00	16:40:00	2024-11-07	6	362
2243	15:00:00	16:40:00	2024-11-14	6	362
2244	15:00:00	16:40:00	2024-11-21	6	362
2245	15:00:00	16:40:00	2024-11-28	6	362
2246	15:00:00	16:40:00	2024-12-05	6	362
2247	15:00:00	16:40:00	2024-12-12	6	362
4674	11:10:00	12:50:00	2024-08-06	30	68
4675	11:10:00	12:50:00	2024-08-13	30	68
4676	11:10:00	12:50:00	2024-08-20	30	68
4677	11:10:00	12:50:00	2024-08-27	30	68
4678	11:10:00	12:50:00	2024-09-03	30	68
4679	11:10:00	12:50:00	2024-09-10	30	68
4680	11:10:00	12:50:00	2024-09-17	30	68
4681	11:10:00	12:50:00	2024-09-24	30	68
4682	11:10:00	12:50:00	2024-10-01	30	68
4683	11:10:00	12:50:00	2024-10-08	30	68
4684	11:10:00	12:50:00	2024-10-15	30	68
4685	11:10:00	12:50:00	2024-10-22	30	68
2096	13:10:00	14:50:00	2024-08-06	4	355
2097	13:10:00	14:50:00	2024-08-13	4	355
2098	13:10:00	14:50:00	2024-08-20	4	355
2099	13:10:00	14:50:00	2024-08-27	4	355
2100	13:10:00	14:50:00	2024-09-03	4	355
2101	13:10:00	14:50:00	2024-09-10	4	355
2102	13:10:00	14:50:00	2024-09-17	4	355
2103	13:10:00	14:50:00	2024-09-24	4	355
2104	13:10:00	14:50:00	2024-10-01	4	355
2105	13:10:00	14:50:00	2024-10-08	4	355
2106	13:10:00	14:50:00	2024-10-15	4	355
2107	13:10:00	14:50:00	2024-10-22	4	355
2108	13:10:00	14:50:00	2024-10-29	4	355
2109	13:10:00	14:50:00	2024-11-05	4	355
2110	13:10:00	14:50:00	2024-11-12	4	355
2111	13:10:00	14:50:00	2024-11-19	4	355
2112	13:10:00	14:50:00	2024-11-26	4	355
2113	13:10:00	14:50:00	2024-12-03	4	355
2114	13:10:00	14:50:00	2024-12-10	4	355
2115	15:00:00	16:40:00	2024-08-08	4	356
2116	15:00:00	16:40:00	2024-08-15	4	356
2117	15:00:00	16:40:00	2024-08-22	4	356
2118	15:00:00	16:40:00	2024-08-29	4	356
2119	15:00:00	16:40:00	2024-09-05	4	356
2120	15:00:00	16:40:00	2024-09-12	4	356
2121	15:00:00	16:40:00	2024-09-19	4	356
2122	15:00:00	16:40:00	2024-09-26	4	356
2123	15:00:00	16:40:00	2024-10-03	4	356
2124	15:00:00	16:40:00	2024-10-10	4	356
2125	15:00:00	16:40:00	2024-10-17	4	356
2126	15:00:00	16:40:00	2024-10-24	4	356
2127	15:00:00	16:40:00	2024-10-31	4	356
2128	15:00:00	16:40:00	2024-11-07	4	356
2129	15:00:00	16:40:00	2024-11-14	4	356
2130	15:00:00	16:40:00	2024-11-21	4	356
2131	15:00:00	16:40:00	2024-11-28	4	356
2132	15:00:00	16:40:00	2024-12-05	4	356
2133	15:00:00	16:40:00	2024-12-12	4	356
2172	13:10:00	14:50:00	2024-08-06	5	359
2173	13:10:00	14:50:00	2024-08-13	5	359
2174	13:10:00	14:50:00	2024-08-20	5	359
2175	13:10:00	14:50:00	2024-08-27	5	359
2176	13:10:00	14:50:00	2024-09-03	5	359
2177	13:10:00	14:50:00	2024-09-10	5	359
2178	13:10:00	14:50:00	2024-09-17	5	359
2179	13:10:00	14:50:00	2024-09-24	5	359
2180	13:10:00	14:50:00	2024-10-01	5	359
2181	13:10:00	14:50:00	2024-10-08	5	359
2182	13:10:00	14:50:00	2024-10-15	5	359
2183	13:10:00	14:50:00	2024-10-22	5	359
2184	13:10:00	14:50:00	2024-10-29	5	359
2185	13:10:00	14:50:00	2024-11-05	5	359
2186	13:10:00	14:50:00	2024-11-12	5	359
2187	13:10:00	14:50:00	2024-11-19	5	359
2188	13:10:00	14:50:00	2024-11-26	5	359
2189	13:10:00	14:50:00	2024-12-03	5	359
2190	13:10:00	14:50:00	2024-12-10	5	359
2191	15:00:00	16:40:00	2024-08-08	5	360
2192	15:00:00	16:40:00	2024-08-15	5	360
2193	15:00:00	16:40:00	2024-08-22	5	360
2194	15:00:00	16:40:00	2024-08-29	5	360
2195	15:00:00	16:40:00	2024-09-05	5	360
2196	15:00:00	16:40:00	2024-09-12	5	360
2197	15:00:00	16:40:00	2024-09-19	5	360
2198	15:00:00	16:40:00	2024-09-26	5	360
2199	15:00:00	16:40:00	2024-10-03	5	360
2200	15:00:00	16:40:00	2024-10-10	5	360
2201	15:00:00	16:40:00	2024-10-17	5	360
2202	15:00:00	16:40:00	2024-10-24	5	360
2203	15:00:00	16:40:00	2024-10-31	5	360
2204	15:00:00	16:40:00	2024-11-07	5	360
2205	15:00:00	16:40:00	2024-11-14	5	360
2206	15:00:00	16:40:00	2024-11-21	5	360
2207	15:00:00	16:40:00	2024-11-28	5	360
2208	15:00:00	16:40:00	2024-12-05	5	360
2209	15:00:00	16:40:00	2024-12-12	5	360
2248	15:00:00	16:40:00	2024-08-06	6	363
2249	15:00:00	16:40:00	2024-08-13	6	363
2250	15:00:00	16:40:00	2024-08-20	6	363
2251	15:00:00	16:40:00	2024-08-27	6	363
2252	15:00:00	16:40:00	2024-09-03	6	363
2253	15:00:00	16:40:00	2024-09-10	6	363
2254	15:00:00	16:40:00	2024-09-17	6	363
2255	15:00:00	16:40:00	2024-09-24	6	363
2256	15:00:00	16:40:00	2024-10-01	6	363
2257	15:00:00	16:40:00	2024-10-08	6	363
2258	15:00:00	16:40:00	2024-10-15	6	363
2259	15:00:00	16:40:00	2024-10-22	6	363
2260	15:00:00	16:40:00	2024-10-29	6	363
2261	15:00:00	16:40:00	2024-11-05	6	363
2262	15:00:00	16:40:00	2024-11-12	6	363
2263	15:00:00	16:40:00	2024-11-19	6	363
2264	15:00:00	16:40:00	2024-11-26	6	363
2265	15:00:00	16:40:00	2024-12-03	6	363
2266	15:00:00	16:40:00	2024-12-10	6	363
2267	13:10:00	14:50:00	2024-08-08	6	364
2268	13:10:00	14:50:00	2024-08-15	6	364
2269	13:10:00	14:50:00	2024-08-22	6	364
2270	13:10:00	14:50:00	2024-08-29	6	364
2271	13:10:00	14:50:00	2024-09-05	6	364
2272	13:10:00	14:50:00	2024-09-12	6	364
2273	13:10:00	14:50:00	2024-09-19	6	364
2274	13:10:00	14:50:00	2024-09-26	6	364
2275	13:10:00	14:50:00	2024-10-03	6	364
2276	13:10:00	14:50:00	2024-10-10	6	364
2277	13:10:00	14:50:00	2024-10-17	6	364
2278	13:10:00	14:50:00	2024-10-24	6	364
2279	13:10:00	14:50:00	2024-10-31	6	364
2280	13:10:00	14:50:00	2024-11-07	6	364
2281	13:10:00	14:50:00	2024-11-14	6	364
2282	13:10:00	14:50:00	2024-11-21	6	364
2283	13:10:00	14:50:00	2024-11-28	6	364
2284	13:10:00	14:50:00	2024-12-05	6	364
2285	13:10:00	14:50:00	2024-12-12	6	364
4686	11:10:00	12:50:00	2024-10-29	30	68
4687	11:10:00	12:50:00	2024-11-05	30	68
4688	11:10:00	12:50:00	2024-11-12	30	68
4689	11:10:00	12:50:00	2024-11-19	30	68
4690	11:10:00	12:50:00	2024-11-26	30	68
4691	11:10:00	12:50:00	2024-12-03	30	68
4692	11:10:00	12:50:00	2024-12-10	30	68
4693	11:10:00	12:50:00	2024-08-08	30	69
4694	11:10:00	12:50:00	2024-08-15	30	69
4695	11:10:00	12:50:00	2024-08-22	30	69
4696	11:10:00	12:50:00	2024-08-29	30	69
4697	11:10:00	12:50:00	2024-09-05	30	69
4698	11:10:00	12:50:00	2024-09-12	30	69
4699	11:10:00	12:50:00	2024-09-19	30	69
4700	11:10:00	12:50:00	2024-09-26	30	69
4701	11:10:00	12:50:00	2024-10-03	30	69
4702	11:10:00	12:50:00	2024-10-10	30	69
4703	11:10:00	12:50:00	2024-10-17	30	69
4704	11:10:00	12:50:00	2024-10-24	30	69
4705	11:10:00	12:50:00	2024-10-31	30	69
4706	11:10:00	12:50:00	2024-11-07	30	69
4707	11:10:00	12:50:00	2024-11-14	30	69
4708	11:10:00	12:50:00	2024-11-21	30	69
4709	11:10:00	12:50:00	2024-11-28	30	69
4710	11:10:00	12:50:00	2024-12-05	30	69
4711	11:10:00	12:50:00	2024-12-12	30	69
4750	11:10:00	12:50:00	2024-08-06	33	72
4751	11:10:00	12:50:00	2024-08-13	33	72
4752	11:10:00	12:50:00	2024-08-20	33	72
4753	11:10:00	12:50:00	2024-08-27	33	72
4754	11:10:00	12:50:00	2024-09-03	33	72
4755	11:10:00	12:50:00	2024-09-10	33	72
4756	11:10:00	12:50:00	2024-09-17	33	72
4757	11:10:00	12:50:00	2024-09-24	33	72
4758	11:10:00	12:50:00	2024-10-01	33	72
4759	11:10:00	12:50:00	2024-10-08	33	72
4760	11:10:00	12:50:00	2024-10-15	33	72
4761	11:10:00	12:50:00	2024-10-22	33	72
4762	11:10:00	12:50:00	2024-10-29	33	72
4763	11:10:00	12:50:00	2024-11-05	33	72
4764	11:10:00	12:50:00	2024-11-12	33	72
4765	11:10:00	12:50:00	2024-11-19	33	72
4766	11:10:00	12:50:00	2024-11-26	33	72
4767	11:10:00	12:50:00	2024-12-03	33	72
4768	11:10:00	12:50:00	2024-12-10	33	72
4769	11:10:00	12:50:00	2024-08-08	33	73
4770	11:10:00	12:50:00	2024-08-15	33	73
4771	11:10:00	12:50:00	2024-08-22	33	73
4772	11:10:00	12:50:00	2024-08-29	33	73
4773	11:10:00	12:50:00	2024-09-05	33	73
4774	11:10:00	12:50:00	2024-09-12	33	73
4775	11:10:00	12:50:00	2024-09-19	33	73
4776	11:10:00	12:50:00	2024-09-26	33	73
4777	11:10:00	12:50:00	2024-10-03	33	73
4778	11:10:00	12:50:00	2024-10-10	33	73
4779	11:10:00	12:50:00	2024-10-17	33	73
4780	11:10:00	12:50:00	2024-10-24	33	73
4781	11:10:00	12:50:00	2024-10-31	33	73
4782	11:10:00	12:50:00	2024-11-07	33	73
4783	11:10:00	12:50:00	2024-11-14	33	73
4784	11:10:00	12:50:00	2024-11-21	33	73
4785	11:10:00	12:50:00	2024-11-28	33	73
4786	11:10:00	12:50:00	2024-12-05	33	73
4787	11:10:00	12:50:00	2024-12-12	33	73
4788	11:10:00	12:50:00	2024-08-05	30	74
4789	11:10:00	12:50:00	2024-08-12	30	74
4790	11:10:00	12:50:00	2024-08-19	30	74
4791	11:10:00	12:50:00	2024-08-26	30	74
4792	11:10:00	12:50:00	2024-09-02	30	74
4793	11:10:00	12:50:00	2024-09-09	30	74
4794	11:10:00	12:50:00	2024-09-16	30	74
4795	11:10:00	12:50:00	2024-09-23	30	74
4796	11:10:00	12:50:00	2024-09-30	30	74
4797	11:10:00	12:50:00	2024-10-07	30	74
4798	11:10:00	12:50:00	2024-10-14	30	74
4799	11:10:00	12:50:00	2024-10-21	30	74
4800	11:10:00	12:50:00	2024-10-28	30	74
4801	11:10:00	12:50:00	2024-11-04	30	74
4802	11:10:00	12:50:00	2024-11-11	30	74
4803	11:10:00	12:50:00	2024-11-18	30	74
4804	11:10:00	12:50:00	2024-11-25	30	74
4805	11:10:00	12:50:00	2024-12-02	30	74
4806	11:10:00	12:50:00	2024-12-09	30	74
4807	11:10:00	12:50:00	2024-08-05	31	75
4808	11:10:00	12:50:00	2024-08-12	31	75
4809	11:10:00	12:50:00	2024-08-19	31	75
4810	11:10:00	12:50:00	2024-08-26	31	75
4811	11:10:00	12:50:00	2024-09-02	31	75
4812	11:10:00	12:50:00	2024-09-09	31	75
4813	11:10:00	12:50:00	2024-09-16	31	75
4814	11:10:00	12:50:00	2024-09-23	31	75
4815	11:10:00	12:50:00	2024-09-30	31	75
4816	11:10:00	12:50:00	2024-10-07	31	75
4817	11:10:00	12:50:00	2024-10-14	31	75
4818	11:10:00	12:50:00	2024-10-21	31	75
4819	11:10:00	12:50:00	2024-10-28	31	75
4820	11:10:00	12:50:00	2024-11-04	31	75
4821	11:10:00	12:50:00	2024-11-11	31	75
4822	11:10:00	12:50:00	2024-11-18	31	75
4823	11:10:00	12:50:00	2024-11-25	31	75
4824	11:10:00	12:50:00	2024-12-02	31	75
4825	11:10:00	12:50:00	2024-12-09	31	75
4826	11:10:00	12:50:00	2024-08-05	33	76
4827	11:10:00	12:50:00	2024-08-12	33	76
4828	11:10:00	12:50:00	2024-08-19	33	76
4829	11:10:00	12:50:00	2024-08-26	33	76
4830	11:10:00	12:50:00	2024-09-02	33	76
4831	11:10:00	12:50:00	2024-09-09	33	76
4832	11:10:00	12:50:00	2024-09-16	33	76
4833	11:10:00	12:50:00	2024-09-23	33	76
4834	11:10:00	12:50:00	2024-09-30	33	76
4835	11:10:00	12:50:00	2024-10-07	33	76
4836	11:10:00	12:50:00	2024-10-14	33	76
4837	11:10:00	12:50:00	2024-10-21	33	76
4838	11:10:00	12:50:00	2024-10-28	33	76
4839	11:10:00	12:50:00	2024-11-04	33	76
4840	11:10:00	12:50:00	2024-11-11	33	76
4841	11:10:00	12:50:00	2024-11-18	33	76
4842	11:10:00	12:50:00	2024-11-25	33	76
4843	11:10:00	12:50:00	2024-12-02	33	76
4844	11:10:00	12:50:00	2024-12-09	33	76
5679	09:20:00	11:00:00	2024-08-05	26	139
5680	09:20:00	11:00:00	2024-08-12	26	139
5681	09:20:00	11:00:00	2024-08-19	26	139
5682	09:20:00	11:00:00	2024-08-26	26	139
5683	09:20:00	11:00:00	2024-09-02	26	139
4712	11:10:00	12:50:00	2024-08-06	31	70
4713	11:10:00	12:50:00	2024-08-13	31	70
4714	11:10:00	12:50:00	2024-08-20	31	70
4715	11:10:00	12:50:00	2024-08-27	31	70
4716	11:10:00	12:50:00	2024-09-03	31	70
4717	11:10:00	12:50:00	2024-09-10	31	70
4718	11:10:00	12:50:00	2024-09-17	31	70
4719	11:10:00	12:50:00	2024-09-24	31	70
4720	11:10:00	12:50:00	2024-10-01	31	70
4721	11:10:00	12:50:00	2024-10-08	31	70
4722	11:10:00	12:50:00	2024-10-15	31	70
4723	11:10:00	12:50:00	2024-10-22	31	70
4724	11:10:00	12:50:00	2024-10-29	31	70
4725	11:10:00	12:50:00	2024-11-05	31	70
4726	11:10:00	12:50:00	2024-11-12	31	70
4727	11:10:00	12:50:00	2024-11-19	31	70
4728	11:10:00	12:50:00	2024-11-26	31	70
4729	11:10:00	12:50:00	2024-12-03	31	70
4730	11:10:00	12:50:00	2024-12-10	31	70
4731	11:10:00	12:50:00	2024-08-08	31	71
4732	11:10:00	12:50:00	2024-08-15	31	71
4733	11:10:00	12:50:00	2024-08-22	31	71
4734	11:10:00	12:50:00	2024-08-29	31	71
4735	11:10:00	12:50:00	2024-09-05	31	71
4736	11:10:00	12:50:00	2024-09-12	31	71
4737	11:10:00	12:50:00	2024-09-19	31	71
2438	08:20:00	11:00:00	2024-08-06	3	371
2439	08:20:00	11:00:00	2024-08-13	3	371
2440	08:20:00	11:00:00	2024-08-20	3	371
2441	08:20:00	11:00:00	2024-08-27	3	371
2442	08:20:00	11:00:00	2024-09-03	3	371
2443	08:20:00	11:00:00	2024-09-10	3	371
2444	08:20:00	11:00:00	2024-09-17	3	371
2445	08:20:00	11:00:00	2024-09-24	3	371
2446	08:20:00	11:00:00	2024-10-01	3	371
2447	08:20:00	11:00:00	2024-10-08	3	371
2448	08:20:00	11:00:00	2024-10-15	3	371
2449	08:20:00	11:00:00	2024-10-22	3	371
2450	08:20:00	11:00:00	2024-10-29	3	371
2451	08:20:00	11:00:00	2024-11-05	3	371
2452	08:20:00	11:00:00	2024-11-12	3	371
2453	08:20:00	11:00:00	2024-11-19	3	371
2454	08:20:00	11:00:00	2024-11-26	3	371
2455	08:20:00	11:00:00	2024-12-03	3	371
2456	08:20:00	11:00:00	2024-12-10	3	371
2457	08:20:00	11:00:00	2024-08-09	3	372
2458	08:20:00	11:00:00	2024-08-16	3	372
2459	08:20:00	11:00:00	2024-08-23	3	372
2460	08:20:00	11:00:00	2024-08-30	3	372
2461	08:20:00	11:00:00	2024-09-06	3	372
2462	08:20:00	11:00:00	2024-09-13	3	372
2463	08:20:00	11:00:00	2024-09-20	3	372
2464	08:20:00	11:00:00	2024-09-27	3	372
2465	08:20:00	11:00:00	2024-10-04	3	372
2466	08:20:00	11:00:00	2024-10-11	3	372
2467	08:20:00	11:00:00	2024-10-18	3	372
2468	08:20:00	11:00:00	2024-10-25	3	372
2469	08:20:00	11:00:00	2024-11-01	3	372
2470	08:20:00	11:00:00	2024-11-08	3	372
2471	08:20:00	11:00:00	2024-11-15	3	372
2472	08:20:00	11:00:00	2024-11-22	3	372
2473	08:20:00	11:00:00	2024-11-29	3	372
2474	08:20:00	11:00:00	2024-12-06	3	372
2475	08:20:00	11:00:00	2024-08-06	4	373
2476	08:20:00	11:00:00	2024-08-13	4	373
2477	08:20:00	11:00:00	2024-08-20	4	373
2478	08:20:00	11:00:00	2024-08-27	4	373
2479	08:20:00	11:00:00	2024-09-03	4	373
2480	08:20:00	11:00:00	2024-09-10	4	373
2481	08:20:00	11:00:00	2024-09-17	4	373
2482	08:20:00	11:00:00	2024-09-24	4	373
2483	08:20:00	11:00:00	2024-10-01	4	373
2484	08:20:00	11:00:00	2024-10-08	4	373
2485	08:20:00	11:00:00	2024-10-15	4	373
2486	08:20:00	11:00:00	2024-10-22	4	373
2487	08:20:00	11:00:00	2024-10-29	4	373
2488	08:20:00	11:00:00	2024-11-05	4	373
2489	08:20:00	11:00:00	2024-11-12	4	373
2490	08:20:00	11:00:00	2024-11-19	4	373
2491	08:20:00	11:00:00	2024-11-26	4	373
2492	08:20:00	11:00:00	2024-12-03	4	373
2493	08:20:00	11:00:00	2024-12-10	4	373
2494	08:20:00	11:00:00	2024-08-09	4	374
2495	08:20:00	11:00:00	2024-08-16	4	374
2496	08:20:00	11:00:00	2024-08-23	4	374
2497	08:20:00	11:00:00	2024-08-30	4	374
2498	08:20:00	11:00:00	2024-09-06	4	374
2499	08:20:00	11:00:00	2024-09-13	4	374
2500	08:20:00	11:00:00	2024-09-20	4	374
2501	08:20:00	11:00:00	2024-09-27	4	374
2502	08:20:00	11:00:00	2024-10-04	4	374
2503	08:20:00	11:00:00	2024-10-11	4	374
2504	08:20:00	11:00:00	2024-10-18	4	374
2505	08:20:00	11:00:00	2024-10-25	4	374
2506	08:20:00	11:00:00	2024-11-01	4	374
2507	08:20:00	11:00:00	2024-11-08	4	374
2508	08:20:00	11:00:00	2024-11-15	4	374
2509	08:20:00	11:00:00	2024-11-22	4	374
2510	08:20:00	11:00:00	2024-11-29	4	374
2511	08:20:00	11:00:00	2024-12-06	4	374
2512	08:20:00	11:00:00	2024-08-06	13	375
2513	08:20:00	11:00:00	2024-08-13	13	375
2514	08:20:00	11:00:00	2024-08-20	13	375
2515	08:20:00	11:00:00	2024-08-27	13	375
2516	08:20:00	11:00:00	2024-09-03	13	375
2517	08:20:00	11:00:00	2024-09-10	13	375
2518	08:20:00	11:00:00	2024-09-17	13	375
2519	08:20:00	11:00:00	2024-09-24	13	375
2520	08:20:00	11:00:00	2024-10-01	13	375
2521	08:20:00	11:00:00	2024-10-08	13	375
2522	08:20:00	11:00:00	2024-10-15	13	375
2523	08:20:00	11:00:00	2024-10-22	13	375
2524	08:20:00	11:00:00	2024-10-29	13	375
2525	08:20:00	11:00:00	2024-11-05	13	375
2526	08:20:00	11:00:00	2024-11-12	13	375
2527	08:20:00	11:00:00	2024-11-19	13	375
2528	08:20:00	11:00:00	2024-11-26	13	375
2529	08:20:00	11:00:00	2024-12-03	13	375
2530	08:20:00	11:00:00	2024-12-10	13	375
2531	08:20:00	11:00:00	2024-08-09	13	376
2532	08:20:00	11:00:00	2024-08-16	13	376
2533	08:20:00	11:00:00	2024-08-23	13	376
2534	08:20:00	11:00:00	2024-08-30	13	376
2535	08:20:00	11:00:00	2024-09-06	13	376
2536	08:20:00	11:00:00	2024-09-13	13	376
2537	08:20:00	11:00:00	2024-09-20	13	376
2538	08:20:00	11:00:00	2024-09-27	13	376
2539	08:20:00	11:00:00	2024-10-04	13	376
2540	08:20:00	11:00:00	2024-10-11	13	376
2541	08:20:00	11:00:00	2024-10-18	13	376
2542	08:20:00	11:00:00	2024-10-25	13	376
2543	08:20:00	11:00:00	2024-11-01	13	376
2544	08:20:00	11:00:00	2024-11-08	13	376
2545	08:20:00	11:00:00	2024-11-15	13	376
2546	08:20:00	11:00:00	2024-11-22	13	376
2547	08:20:00	11:00:00	2024-11-29	13	376
2548	08:20:00	11:00:00	2024-12-06	13	376
2549	08:20:00	11:00:00	2024-08-06	12	377
2550	08:20:00	11:00:00	2024-08-13	12	377
2551	08:20:00	11:00:00	2024-08-20	12	377
2552	08:20:00	11:00:00	2024-08-27	12	377
2553	08:20:00	11:00:00	2024-09-03	12	377
2554	08:20:00	11:00:00	2024-09-10	12	377
2555	08:20:00	11:00:00	2024-09-17	12	377
2556	08:20:00	11:00:00	2024-09-24	12	377
2557	08:20:00	11:00:00	2024-10-01	12	377
2558	08:20:00	11:00:00	2024-10-08	12	377
2559	08:20:00	11:00:00	2024-10-15	12	377
2560	08:20:00	11:00:00	2024-10-22	12	377
2561	08:20:00	11:00:00	2024-10-29	12	377
2562	08:20:00	11:00:00	2024-11-05	12	377
2563	08:20:00	11:00:00	2024-11-12	12	377
2564	08:20:00	11:00:00	2024-11-19	12	377
2565	08:20:00	11:00:00	2024-11-26	12	377
2566	08:20:00	11:00:00	2024-12-03	12	377
2567	08:20:00	11:00:00	2024-12-10	12	377
2568	08:20:00	11:00:00	2024-08-09	12	378
2569	08:20:00	11:00:00	2024-08-16	12	378
2570	08:20:00	11:00:00	2024-08-23	12	378
2571	08:20:00	11:00:00	2024-08-30	12	378
2572	08:20:00	11:00:00	2024-09-06	12	378
2573	08:20:00	11:00:00	2024-09-13	12	378
2574	08:20:00	11:00:00	2024-09-20	12	378
2575	08:20:00	11:00:00	2024-09-27	12	378
2576	08:20:00	11:00:00	2024-10-04	12	378
2577	08:20:00	11:00:00	2024-10-11	12	378
2578	08:20:00	11:00:00	2024-10-18	12	378
2579	08:20:00	11:00:00	2024-10-25	12	378
2580	08:20:00	11:00:00	2024-11-01	12	378
2581	08:20:00	11:00:00	2024-11-08	12	378
2582	08:20:00	11:00:00	2024-11-15	12	378
2583	08:20:00	11:00:00	2024-11-22	12	378
2584	08:20:00	11:00:00	2024-11-29	12	378
2585	08:20:00	11:00:00	2024-12-06	12	378
2586	08:20:00	11:00:00	2024-08-06	11	379
2587	08:20:00	11:00:00	2024-08-13	11	379
2588	08:20:00	11:00:00	2024-08-20	11	379
2589	08:20:00	11:00:00	2024-08-27	11	379
2590	08:20:00	11:00:00	2024-09-03	11	379
2591	08:20:00	11:00:00	2024-09-10	11	379
2592	08:20:00	11:00:00	2024-09-17	11	379
2593	08:20:00	11:00:00	2024-09-24	11	379
2594	08:20:00	11:00:00	2024-10-01	11	379
2595	08:20:00	11:00:00	2024-10-08	11	379
2596	08:20:00	11:00:00	2024-10-15	11	379
2597	08:20:00	11:00:00	2024-10-22	11	379
2598	08:20:00	11:00:00	2024-10-29	11	379
2599	08:20:00	11:00:00	2024-11-05	11	379
2600	08:20:00	11:00:00	2024-11-12	11	379
2601	08:20:00	11:00:00	2024-11-19	11	379
2602	08:20:00	11:00:00	2024-11-26	11	379
2603	08:20:00	11:00:00	2024-12-03	11	379
2604	08:20:00	11:00:00	2024-12-10	11	379
2605	08:20:00	11:00:00	2024-08-09	11	380
2606	08:20:00	11:00:00	2024-08-16	11	380
2607	08:20:00	11:00:00	2024-08-23	11	380
2608	08:20:00	11:00:00	2024-08-30	11	380
2609	08:20:00	11:00:00	2024-09-06	11	380
2610	08:20:00	11:00:00	2024-09-13	11	380
2611	08:20:00	11:00:00	2024-09-20	11	380
2612	08:20:00	11:00:00	2024-09-27	11	380
2613	08:20:00	11:00:00	2024-10-04	11	380
2614	08:20:00	11:00:00	2024-10-11	11	380
2615	08:20:00	11:00:00	2024-10-18	11	380
2616	08:20:00	11:00:00	2024-10-25	11	380
2617	08:20:00	11:00:00	2024-11-01	11	380
2618	08:20:00	11:00:00	2024-11-08	11	380
2619	08:20:00	11:00:00	2024-11-15	11	380
2620	08:20:00	11:00:00	2024-11-22	11	380
2621	08:20:00	11:00:00	2024-11-29	11	380
2622	08:20:00	11:00:00	2024-12-06	11	380
2623	08:20:00	11:00:00	2024-08-06	10	381
2624	08:20:00	11:00:00	2024-08-13	10	381
2625	08:20:00	11:00:00	2024-08-20	10	381
2626	08:20:00	11:00:00	2024-08-27	10	381
2627	08:20:00	11:00:00	2024-09-03	10	381
2628	08:20:00	11:00:00	2024-09-10	10	381
2629	08:20:00	11:00:00	2024-09-17	10	381
2630	08:20:00	11:00:00	2024-09-24	10	381
2631	08:20:00	11:00:00	2024-10-01	10	381
2632	08:20:00	11:00:00	2024-10-08	10	381
2633	08:20:00	11:00:00	2024-10-15	10	381
2634	08:20:00	11:00:00	2024-10-22	10	381
2635	08:20:00	11:00:00	2024-10-29	10	381
2636	08:20:00	11:00:00	2024-11-05	10	381
2637	08:20:00	11:00:00	2024-11-12	10	381
2638	08:20:00	11:00:00	2024-11-19	10	381
2639	08:20:00	11:00:00	2024-11-26	10	381
2640	08:20:00	11:00:00	2024-12-03	10	381
2641	08:20:00	11:00:00	2024-12-10	10	381
2642	08:20:00	11:00:00	2024-08-09	10	382
2643	08:20:00	11:00:00	2024-08-16	10	382
2644	08:20:00	11:00:00	2024-08-23	10	382
2645	08:20:00	11:00:00	2024-08-30	10	382
2646	08:20:00	11:00:00	2024-09-06	10	382
2647	08:20:00	11:00:00	2024-09-13	10	382
2648	08:20:00	11:00:00	2024-09-20	10	382
2649	08:20:00	11:00:00	2024-09-27	10	382
2650	08:20:00	11:00:00	2024-10-04	10	382
2651	08:20:00	11:00:00	2024-10-11	10	382
2652	08:20:00	11:00:00	2024-10-18	10	382
2653	08:20:00	11:00:00	2024-10-25	10	382
2654	08:20:00	11:00:00	2024-11-01	10	382
2655	08:20:00	11:00:00	2024-11-08	10	382
2656	08:20:00	11:00:00	2024-11-15	10	382
2657	08:20:00	11:00:00	2024-11-22	10	382
2658	08:20:00	11:00:00	2024-11-29	10	382
2659	08:20:00	11:00:00	2024-12-06	10	382
2698	08:20:00	11:00:00	2024-08-05	11	387
2699	08:20:00	11:00:00	2024-08-12	11	387
2700	08:20:00	11:00:00	2024-08-19	11	387
2701	08:20:00	11:00:00	2024-08-26	11	387
2702	08:20:00	11:00:00	2024-09-02	11	387
2703	08:20:00	11:00:00	2024-09-09	11	387
2704	08:20:00	11:00:00	2024-09-16	11	387
2705	08:20:00	11:00:00	2024-09-23	11	387
2706	08:20:00	11:00:00	2024-09-30	11	387
2707	08:20:00	11:00:00	2024-10-07	11	387
2708	08:20:00	11:00:00	2024-10-14	11	387
2709	08:20:00	11:00:00	2024-10-21	11	387
2710	08:20:00	11:00:00	2024-10-28	11	387
2711	08:20:00	11:00:00	2024-11-04	11	387
2712	08:20:00	11:00:00	2024-11-11	11	387
2713	08:20:00	11:00:00	2024-11-18	11	387
2714	08:20:00	11:00:00	2024-11-25	11	387
2715	08:20:00	11:00:00	2024-12-02	11	387
2716	08:20:00	11:00:00	2024-12-09	11	387
2717	08:20:00	11:00:00	2024-08-07	11	388
2718	08:20:00	11:00:00	2024-08-14	11	388
2719	08:20:00	11:00:00	2024-08-21	11	388
2720	08:20:00	11:00:00	2024-08-28	11	388
2721	08:20:00	11:00:00	2024-09-04	11	388
2722	08:20:00	11:00:00	2024-09-11	11	388
2723	08:20:00	11:00:00	2024-09-18	11	388
2724	08:20:00	11:00:00	2024-09-25	11	388
2725	08:20:00	11:00:00	2024-10-02	11	388
2726	08:20:00	11:00:00	2024-10-09	11	388
2727	08:20:00	11:00:00	2024-10-16	11	388
2728	08:20:00	11:00:00	2024-10-23	11	388
2729	08:20:00	11:00:00	2024-10-30	11	388
2730	08:20:00	11:00:00	2024-11-06	11	388
2731	08:20:00	11:00:00	2024-11-13	11	388
2732	08:20:00	11:00:00	2024-11-20	11	388
2733	08:20:00	11:00:00	2024-11-27	11	388
2734	08:20:00	11:00:00	2024-12-04	11	388
2735	08:20:00	11:00:00	2024-12-11	11	388
2774	08:20:00	11:00:00	2024-08-06	8	391
2775	08:20:00	11:00:00	2024-08-13	8	391
2776	08:20:00	11:00:00	2024-08-20	8	391
2777	08:20:00	11:00:00	2024-08-27	8	391
2778	08:20:00	11:00:00	2024-09-03	8	391
2779	08:20:00	11:00:00	2024-09-10	8	391
2780	08:20:00	11:00:00	2024-09-17	8	391
2781	08:20:00	11:00:00	2024-09-24	8	391
2782	08:20:00	11:00:00	2024-10-01	8	391
2783	08:20:00	11:00:00	2024-10-08	8	391
2784	08:20:00	11:00:00	2024-10-15	8	391
2785	08:20:00	11:00:00	2024-10-22	8	391
2786	08:20:00	11:00:00	2024-10-29	8	391
2787	08:20:00	11:00:00	2024-11-05	8	391
2788	08:20:00	11:00:00	2024-11-12	8	391
2789	08:20:00	11:00:00	2024-11-19	8	391
2790	08:20:00	11:00:00	2024-11-26	8	391
2791	08:20:00	11:00:00	2024-12-03	8	391
2792	08:20:00	11:00:00	2024-12-10	8	391
2793	08:20:00	11:00:00	2024-08-09	8	392
2794	08:20:00	11:00:00	2024-08-16	8	392
2795	08:20:00	11:00:00	2024-08-23	8	392
2796	08:20:00	11:00:00	2024-08-30	8	392
2797	08:20:00	11:00:00	2024-09-06	8	392
2798	08:20:00	11:00:00	2024-09-13	8	392
2799	08:20:00	11:00:00	2024-09-20	8	392
2800	08:20:00	11:00:00	2024-09-27	8	392
2801	08:20:00	11:00:00	2024-10-04	8	392
2802	08:20:00	11:00:00	2024-10-11	8	392
2803	08:20:00	11:00:00	2024-10-18	8	392
2804	08:20:00	11:00:00	2024-10-25	8	392
2805	08:20:00	11:00:00	2024-11-01	8	392
2806	08:20:00	11:00:00	2024-11-08	8	392
2807	08:20:00	11:00:00	2024-11-15	8	392
2808	08:20:00	11:00:00	2024-11-22	8	392
2809	08:20:00	11:00:00	2024-11-29	8	392
2810	08:20:00	11:00:00	2024-12-06	8	392
4738	11:10:00	12:50:00	2024-09-26	31	71
4739	11:10:00	12:50:00	2024-10-03	31	71
4740	11:10:00	12:50:00	2024-10-10	31	71
4741	11:10:00	12:50:00	2024-10-17	31	71
4742	11:10:00	12:50:00	2024-10-24	31	71
4743	11:10:00	12:50:00	2024-10-31	31	71
4744	11:10:00	12:50:00	2024-11-07	31	71
4745	11:10:00	12:50:00	2024-11-14	31	71
4746	11:10:00	12:50:00	2024-11-21	31	71
4747	11:10:00	12:50:00	2024-11-28	31	71
4748	11:10:00	12:50:00	2024-12-05	31	71
4749	11:10:00	12:50:00	2024-12-12	31	71
5087	08:20:00	10:00:00	2024-05-07	23	90
5088	08:20:00	10:00:00	2024-05-14	23	90
5089	08:20:00	10:00:00	2024-05-21	23	90
5090	08:20:00	10:00:00	2024-05-28	23	90
5091	08:20:00	10:00:00	2024-06-04	23	90
5092	08:20:00	10:00:00	2024-06-11	23	90
5093	08:20:00	10:00:00	2024-06-18	23	90
5094	08:20:00	10:00:00	2024-06-25	23	90
5095	08:20:00	10:00:00	2024-07-02	23	90
5096	08:20:00	10:00:00	2024-07-09	23	90
5097	08:20:00	10:00:00	2024-07-16	23	90
5098	08:20:00	10:00:00	2024-07-23	23	90
5099	08:20:00	10:00:00	2024-07-30	23	90
5100	08:20:00	10:00:00	2024-08-06	23	90
5101	08:20:00	10:00:00	2024-08-13	23	90
5102	08:20:00	10:00:00	2024-05-09	23	91
5103	08:20:00	10:00:00	2024-05-16	23	91
5104	08:20:00	10:00:00	2024-05-23	23	91
5105	08:20:00	10:00:00	2024-05-30	23	91
5106	08:20:00	10:00:00	2024-06-06	23	91
5107	08:20:00	10:00:00	2024-06-13	23	91
5108	08:20:00	10:00:00	2024-06-20	23	91
5109	08:20:00	10:00:00	2024-06-27	23	91
5110	08:20:00	10:00:00	2024-07-04	23	91
5111	08:20:00	10:00:00	2024-07-11	23	91
2660	08:20:00	11:00:00	2024-08-05	10	385
2661	08:20:00	11:00:00	2024-08-12	10	385
2662	08:20:00	11:00:00	2024-08-19	10	385
2663	08:20:00	11:00:00	2024-08-26	10	385
2664	08:20:00	11:00:00	2024-09-02	10	385
2665	08:20:00	11:00:00	2024-09-09	10	385
2666	08:20:00	11:00:00	2024-09-16	10	385
2667	08:20:00	11:00:00	2024-09-23	10	385
2668	08:20:00	11:00:00	2024-09-30	10	385
2669	08:20:00	11:00:00	2024-10-07	10	385
2670	08:20:00	11:00:00	2024-10-14	10	385
2671	08:20:00	11:00:00	2024-10-21	10	385
2672	08:20:00	11:00:00	2024-10-28	10	385
2673	08:20:00	11:00:00	2024-11-04	10	385
2674	08:20:00	11:00:00	2024-11-11	10	385
2675	08:20:00	11:00:00	2024-11-18	10	385
2676	08:20:00	11:00:00	2024-11-25	10	385
2677	08:20:00	11:00:00	2024-12-02	10	385
2678	08:20:00	11:00:00	2024-12-09	10	385
2679	08:20:00	11:00:00	2024-08-07	10	386
2680	08:20:00	11:00:00	2024-08-14	10	386
2681	08:20:00	11:00:00	2024-08-21	10	386
2682	08:20:00	11:00:00	2024-08-28	10	386
2683	08:20:00	11:00:00	2024-09-04	10	386
2684	08:20:00	11:00:00	2024-09-11	10	386
2685	08:20:00	11:00:00	2024-09-18	10	386
2686	08:20:00	11:00:00	2024-09-25	10	386
2687	08:20:00	11:00:00	2024-10-02	10	386
2688	08:20:00	11:00:00	2024-10-09	10	386
2689	08:20:00	11:00:00	2024-10-16	10	386
2690	08:20:00	11:00:00	2024-10-23	10	386
2691	08:20:00	11:00:00	2024-10-30	10	386
2692	08:20:00	11:00:00	2024-11-06	10	386
2693	08:20:00	11:00:00	2024-11-13	10	386
2694	08:20:00	11:00:00	2024-11-20	10	386
2695	08:20:00	11:00:00	2024-11-27	10	386
2696	08:20:00	11:00:00	2024-12-04	10	386
2697	08:20:00	11:00:00	2024-12-11	10	386
2736	08:20:00	11:00:00	2024-08-05	13	389
2737	08:20:00	11:00:00	2024-08-12	13	389
2738	08:20:00	11:00:00	2024-08-19	13	389
2739	08:20:00	11:00:00	2024-08-26	13	389
2740	08:20:00	11:00:00	2024-09-02	13	389
2741	08:20:00	11:00:00	2024-09-09	13	389
2742	08:20:00	11:00:00	2024-09-16	13	389
2743	08:20:00	11:00:00	2024-09-23	13	389
2744	08:20:00	11:00:00	2024-09-30	13	389
2745	08:20:00	11:00:00	2024-10-07	13	389
2746	08:20:00	11:00:00	2024-10-14	13	389
2747	08:20:00	11:00:00	2024-10-21	13	389
2748	08:20:00	11:00:00	2024-10-28	13	389
2749	08:20:00	11:00:00	2024-11-04	13	389
2750	08:20:00	11:00:00	2024-11-11	13	389
2751	08:20:00	11:00:00	2024-11-18	13	389
2752	08:20:00	11:00:00	2024-11-25	13	389
2753	08:20:00	11:00:00	2024-12-02	13	389
2754	08:20:00	11:00:00	2024-12-09	13	389
2755	08:20:00	11:00:00	2024-08-07	13	390
2756	08:20:00	11:00:00	2024-08-14	13	390
2757	08:20:00	11:00:00	2024-08-21	13	390
2758	08:20:00	11:00:00	2024-08-28	13	390
2759	08:20:00	11:00:00	2024-09-04	13	390
2760	08:20:00	11:00:00	2024-09-11	13	390
2761	08:20:00	11:00:00	2024-09-18	13	390
2762	08:20:00	11:00:00	2024-09-25	13	390
2763	08:20:00	11:00:00	2024-10-02	13	390
2764	08:20:00	11:00:00	2024-10-09	13	390
2765	08:20:00	11:00:00	2024-10-16	13	390
2766	08:20:00	11:00:00	2024-10-23	13	390
2767	08:20:00	11:00:00	2024-10-30	13	390
2768	08:20:00	11:00:00	2024-11-06	13	390
2769	08:20:00	11:00:00	2024-11-13	13	390
2770	08:20:00	11:00:00	2024-11-20	13	390
2771	08:20:00	11:00:00	2024-11-27	13	390
2772	08:20:00	11:00:00	2024-12-04	13	390
2773	08:20:00	11:00:00	2024-12-11	13	390
2811	08:20:00	11:00:00	2024-08-06	9	393
2812	08:20:00	11:00:00	2024-08-13	9	393
2813	08:20:00	11:00:00	2024-08-20	9	393
2814	08:20:00	11:00:00	2024-08-27	9	393
2815	08:20:00	11:00:00	2024-09-03	9	393
2816	08:20:00	11:00:00	2024-09-10	9	393
2817	08:20:00	11:00:00	2024-09-17	9	393
2818	08:20:00	11:00:00	2024-09-24	9	393
2819	08:20:00	11:00:00	2024-10-01	9	393
2820	08:20:00	11:00:00	2024-10-08	9	393
2821	08:20:00	11:00:00	2024-10-15	9	393
2822	08:20:00	11:00:00	2024-10-22	9	393
2823	08:20:00	11:00:00	2024-10-29	9	393
2824	08:20:00	11:00:00	2024-11-05	9	393
2825	08:20:00	11:00:00	2024-11-12	9	393
2826	08:20:00	11:00:00	2024-11-19	9	393
2827	08:20:00	11:00:00	2024-11-26	9	393
2828	08:20:00	11:00:00	2024-12-03	9	393
2829	08:20:00	11:00:00	2024-12-10	9	393
2830	08:20:00	11:00:00	2024-08-09	9	394
2831	08:20:00	11:00:00	2024-08-16	9	394
2832	08:20:00	11:00:00	2024-08-23	9	394
2833	08:20:00	11:00:00	2024-08-30	9	394
2834	08:20:00	11:00:00	2024-09-06	9	394
2835	08:20:00	11:00:00	2024-09-13	9	394
2836	08:20:00	11:00:00	2024-09-20	9	394
2837	08:20:00	11:00:00	2024-09-27	9	394
2838	08:20:00	11:00:00	2024-10-04	9	394
2839	08:20:00	11:00:00	2024-10-11	9	394
2840	08:20:00	11:00:00	2024-10-18	9	394
2841	08:20:00	11:00:00	2024-10-25	9	394
2842	08:20:00	11:00:00	2024-11-01	9	394
2843	08:20:00	11:00:00	2024-11-08	9	394
2844	08:20:00	11:00:00	2024-11-15	9	394
2845	08:20:00	11:00:00	2024-11-22	9	394
2846	08:20:00	11:00:00	2024-11-29	9	394
2847	08:20:00	11:00:00	2024-12-06	9	394
4845	07:30:00	11:00:00	2024-08-07	72	77
4846	07:30:00	11:00:00	2024-08-14	72	77
4847	07:30:00	11:00:00	2024-08-21	72	77
4848	07:30:00	11:00:00	2024-08-28	72	77
4849	07:30:00	11:00:00	2024-09-04	72	77
4850	07:30:00	11:00:00	2024-09-11	72	77
4851	07:30:00	11:00:00	2024-09-18	72	77
4852	07:30:00	11:00:00	2024-09-25	72	77
4853	07:30:00	11:00:00	2024-10-02	72	77
4854	07:30:00	11:00:00	2024-10-09	72	77
4855	07:30:00	11:00:00	2024-10-16	72	77
4856	07:30:00	11:00:00	2024-10-23	72	77
4857	07:30:00	11:00:00	2024-10-30	72	77
4858	07:30:00	11:00:00	2024-11-06	72	77
4859	07:30:00	11:00:00	2024-11-13	72	77
4860	07:30:00	11:00:00	2024-11-20	72	77
4861	07:30:00	11:00:00	2024-11-27	72	77
4862	07:30:00	11:00:00	2024-12-04	72	77
4863	07:30:00	11:00:00	2024-12-11	72	77
4902	15:50:00	17:30:00	2024-08-06	21	80
4903	15:50:00	17:30:00	2024-08-13	21	80
4904	15:50:00	17:30:00	2024-08-20	21	80
4905	15:50:00	17:30:00	2024-08-27	21	80
4906	15:50:00	17:30:00	2024-09-03	21	80
4907	15:50:00	17:30:00	2024-09-10	21	80
4908	15:50:00	17:30:00	2024-09-17	21	80
4909	15:50:00	17:30:00	2024-09-24	21	80
4910	15:50:00	17:30:00	2024-10-01	21	80
4911	15:50:00	17:30:00	2024-10-08	21	80
4912	15:50:00	17:30:00	2024-10-15	21	80
4913	15:50:00	17:30:00	2024-10-22	21	80
4914	15:50:00	17:30:00	2024-10-29	21	80
4915	15:50:00	17:30:00	2024-11-05	21	80
4916	15:50:00	17:30:00	2024-11-12	21	80
4917	15:50:00	17:30:00	2024-11-19	21	80
4918	15:50:00	17:30:00	2024-11-26	21	80
4919	15:50:00	17:30:00	2024-12-03	21	80
4920	15:50:00	17:30:00	2024-12-10	21	80
4921	15:50:00	17:30:00	2024-08-08	21	81
4922	15:50:00	17:30:00	2024-08-15	21	81
4923	15:50:00	17:30:00	2024-08-22	21	81
4924	15:50:00	17:30:00	2024-08-29	21	81
4925	15:50:00	17:30:00	2024-09-05	21	81
4926	15:50:00	17:30:00	2024-09-12	21	81
4927	15:50:00	17:30:00	2024-09-19	21	81
4928	15:50:00	17:30:00	2024-09-26	21	81
4929	15:50:00	17:30:00	2024-10-03	21	81
4930	15:50:00	17:30:00	2024-10-10	21	81
4931	15:50:00	17:30:00	2024-10-17	21	81
4932	15:50:00	17:30:00	2024-10-24	21	81
4933	15:50:00	17:30:00	2024-10-31	21	81
4934	15:50:00	17:30:00	2024-11-07	21	81
4935	15:50:00	17:30:00	2024-11-14	21	81
4936	15:50:00	17:30:00	2024-11-21	21	81
4937	15:50:00	17:30:00	2024-11-28	21	81
4938	15:50:00	17:30:00	2024-12-05	21	81
4939	15:50:00	17:30:00	2024-12-12	21	81
5684	09:20:00	11:00:00	2024-09-09	26	139
5685	09:20:00	11:00:00	2024-09-16	26	139
5686	09:20:00	11:00:00	2024-09-23	26	139
5687	09:20:00	11:00:00	2024-09-30	26	139
5688	09:20:00	11:00:00	2024-10-07	26	139
5689	09:20:00	11:00:00	2024-10-14	26	139
5690	09:20:00	11:00:00	2024-10-21	26	139
5691	09:20:00	11:00:00	2024-10-28	26	139
5692	09:20:00	11:00:00	2024-11-04	26	139
5693	09:20:00	11:00:00	2024-11-11	26	139
5694	09:20:00	11:00:00	2024-11-18	26	139
5695	09:20:00	11:00:00	2024-11-25	26	139
5696	09:20:00	11:00:00	2024-12-02	26	139
5697	09:20:00	11:00:00	2024-12-09	26	139
5698	09:20:00	11:00:00	2024-08-07	22	140
5699	09:20:00	11:00:00	2024-08-14	22	140
5700	09:20:00	11:00:00	2024-08-21	22	140
5701	09:20:00	11:00:00	2024-08-28	22	140
5702	09:20:00	11:00:00	2024-09-04	22	140
2924	15:00:00	16:40:00	2024-08-05	10	399
2925	15:00:00	16:40:00	2024-08-12	10	399
2926	15:00:00	16:40:00	2024-08-19	10	399
2927	15:00:00	16:40:00	2024-08-26	10	399
2928	15:00:00	16:40:00	2024-09-02	10	399
2929	15:00:00	16:40:00	2024-09-09	10	399
2930	15:00:00	16:40:00	2024-09-16	10	399
2931	15:00:00	16:40:00	2024-09-23	10	399
2932	15:00:00	16:40:00	2024-09-30	10	399
2933	15:00:00	16:40:00	2024-10-07	10	399
2934	15:00:00	16:40:00	2024-10-14	10	399
2935	15:00:00	16:40:00	2024-10-21	10	399
2936	15:00:00	16:40:00	2024-10-28	10	399
2937	15:00:00	16:40:00	2024-11-04	10	399
2938	15:00:00	16:40:00	2024-11-11	10	399
2939	15:00:00	16:40:00	2024-11-18	10	399
2940	15:00:00	16:40:00	2024-11-25	10	399
2941	15:00:00	16:40:00	2024-12-02	10	399
2942	15:00:00	16:40:00	2024-12-09	10	399
2943	13:10:00	14:50:00	2024-08-05	8	400
2944	13:10:00	14:50:00	2024-08-12	8	400
2945	13:10:00	14:50:00	2024-08-19	8	400
2946	13:10:00	14:50:00	2024-08-26	8	400
2947	13:10:00	14:50:00	2024-09-02	8	400
2948	13:10:00	14:50:00	2024-09-09	8	400
2949	13:10:00	14:50:00	2024-09-16	8	400
2950	13:10:00	14:50:00	2024-09-23	8	400
2951	13:10:00	14:50:00	2024-09-30	8	400
2952	13:10:00	14:50:00	2024-10-07	8	400
2953	13:10:00	14:50:00	2024-10-14	8	400
2954	13:10:00	14:50:00	2024-10-21	8	400
2955	13:10:00	14:50:00	2024-10-28	8	400
2956	13:10:00	14:50:00	2024-11-04	8	400
2957	13:10:00	14:50:00	2024-11-11	8	400
2958	13:10:00	14:50:00	2024-11-18	8	400
2959	13:10:00	14:50:00	2024-11-25	8	400
2960	13:10:00	14:50:00	2024-12-02	8	400
2961	13:10:00	14:50:00	2024-12-09	8	400
2962	15:00:00	16:40:00	2024-08-05	9	401
2963	15:00:00	16:40:00	2024-08-12	9	401
2964	15:00:00	16:40:00	2024-08-19	9	401
2965	15:00:00	16:40:00	2024-08-26	9	401
2966	15:00:00	16:40:00	2024-09-02	9	401
2967	15:00:00	16:40:00	2024-09-09	9	401
2968	15:00:00	16:40:00	2024-09-16	9	401
2969	15:00:00	16:40:00	2024-09-23	9	401
2970	15:00:00	16:40:00	2024-09-30	9	401
2971	15:00:00	16:40:00	2024-10-07	9	401
2972	15:00:00	16:40:00	2024-10-14	9	401
2973	15:00:00	16:40:00	2024-10-21	9	401
2974	15:00:00	16:40:00	2024-10-28	9	401
2975	15:00:00	16:40:00	2024-11-04	9	401
2976	15:00:00	16:40:00	2024-11-11	9	401
2977	15:00:00	16:40:00	2024-11-18	9	401
2978	15:00:00	16:40:00	2024-11-25	9	401
2979	15:00:00	16:40:00	2024-12-02	9	401
2980	15:00:00	16:40:00	2024-12-09	9	401
2981	13:10:00	14:50:00	2024-08-05	9	402
2982	13:10:00	14:50:00	2024-08-12	9	402
2983	13:10:00	14:50:00	2024-08-19	9	402
2984	13:10:00	14:50:00	2024-08-26	9	402
2985	13:10:00	14:50:00	2024-09-02	9	402
2986	13:10:00	14:50:00	2024-09-09	9	402
2987	13:10:00	14:50:00	2024-09-16	9	402
2988	13:10:00	14:50:00	2024-09-23	9	402
2989	13:10:00	14:50:00	2024-09-30	9	402
2990	13:10:00	14:50:00	2024-10-07	9	402
2991	13:10:00	14:50:00	2024-10-14	9	402
2992	13:10:00	14:50:00	2024-10-21	9	402
2993	13:10:00	14:50:00	2024-10-28	9	402
2994	13:10:00	14:50:00	2024-11-04	9	402
2995	13:10:00	14:50:00	2024-11-11	9	402
2996	13:10:00	14:50:00	2024-11-18	9	402
2997	13:10:00	14:50:00	2024-11-25	9	402
2998	13:10:00	14:50:00	2024-12-02	9	402
2999	13:10:00	14:50:00	2024-12-09	9	402
3000	13:10:00	14:50:00	2024-08-05	12	403
3001	13:10:00	14:50:00	2024-08-12	12	403
3002	13:10:00	14:50:00	2024-08-19	12	403
3003	13:10:00	14:50:00	2024-08-26	12	403
3004	13:10:00	14:50:00	2024-09-02	12	403
3005	13:10:00	14:50:00	2024-09-09	12	403
3006	13:10:00	14:50:00	2024-09-16	12	403
3007	13:10:00	14:50:00	2024-09-23	12	403
3008	13:10:00	14:50:00	2024-09-30	12	403
3009	13:10:00	14:50:00	2024-10-07	12	403
3010	13:10:00	14:50:00	2024-10-14	12	403
3011	13:10:00	14:50:00	2024-10-21	12	403
3012	13:10:00	14:50:00	2024-10-28	12	403
3013	13:10:00	14:50:00	2024-11-04	12	403
3014	13:10:00	14:50:00	2024-11-11	12	403
3015	13:10:00	14:50:00	2024-11-18	12	403
3016	13:10:00	14:50:00	2024-11-25	12	403
3017	13:10:00	14:50:00	2024-12-02	12	403
3018	13:10:00	14:50:00	2024-12-09	12	403
4864	14:00:00	15:40:00	2024-08-05	21	78
4865	14:00:00	15:40:00	2024-08-12	21	78
4866	14:00:00	15:40:00	2024-08-19	21	78
4867	14:00:00	15:40:00	2024-08-26	21	78
4868	14:00:00	15:40:00	2024-09-02	21	78
4869	14:00:00	15:40:00	2024-09-09	21	78
4870	14:00:00	15:40:00	2024-09-16	21	78
4871	14:00:00	15:40:00	2024-09-23	21	78
4872	14:00:00	15:40:00	2024-09-30	21	78
4873	14:00:00	15:40:00	2024-10-07	21	78
4874	14:00:00	15:40:00	2024-10-14	21	78
4875	14:00:00	15:40:00	2024-10-21	21	78
4876	14:00:00	15:40:00	2024-10-28	21	78
4877	14:00:00	15:40:00	2024-11-04	21	78
4878	14:00:00	15:40:00	2024-11-11	21	78
4879	14:00:00	15:40:00	2024-11-18	21	78
4880	14:00:00	15:40:00	2024-11-25	21	78
4881	14:00:00	15:40:00	2024-12-02	21	78
4882	14:00:00	15:40:00	2024-12-09	21	78
4883	14:00:00	15:40:00	2024-08-07	21	79
4884	14:00:00	15:40:00	2024-08-14	21	79
4885	14:00:00	15:40:00	2024-08-21	21	79
4886	14:00:00	15:40:00	2024-08-28	21	79
4887	14:00:00	15:40:00	2024-09-04	21	79
4888	14:00:00	15:40:00	2024-09-11	21	79
4889	14:00:00	15:40:00	2024-09-18	21	79
4890	14:00:00	15:40:00	2024-09-25	21	79
4891	14:00:00	15:40:00	2024-10-02	21	79
4892	14:00:00	15:40:00	2024-10-09	21	79
4893	14:00:00	15:40:00	2024-10-16	21	79
4894	14:00:00	15:40:00	2024-10-23	21	79
4895	14:00:00	15:40:00	2024-10-30	21	79
4896	14:00:00	15:40:00	2024-11-06	21	79
4897	14:00:00	15:40:00	2024-11-13	21	79
4898	14:00:00	15:40:00	2024-11-20	21	79
4899	14:00:00	15:40:00	2024-11-27	21	79
4900	14:00:00	15:40:00	2024-12-04	21	79
4901	14:00:00	15:40:00	2024-12-11	21	79
4940	14:00:00	15:40:00	2024-08-06	21	82
4941	14:00:00	15:40:00	2024-08-13	21	82
4942	14:00:00	15:40:00	2024-08-20	21	82
4943	14:00:00	15:40:00	2024-08-27	21	82
4944	14:00:00	15:40:00	2024-09-03	21	82
4945	14:00:00	15:40:00	2024-09-10	21	82
4946	14:00:00	15:40:00	2024-09-17	21	82
4947	14:00:00	15:40:00	2024-09-24	21	82
4948	14:00:00	15:40:00	2024-10-01	21	82
4949	14:00:00	15:40:00	2024-10-08	21	82
4950	14:00:00	15:40:00	2024-10-15	21	82
4951	14:00:00	15:40:00	2024-10-22	21	82
4952	14:00:00	15:40:00	2024-10-29	21	82
4953	14:00:00	15:40:00	2024-11-05	21	82
4954	14:00:00	15:40:00	2024-11-12	21	82
4955	14:00:00	15:40:00	2024-11-19	21	82
4956	14:00:00	15:40:00	2024-11-26	21	82
4957	14:00:00	15:40:00	2024-12-03	21	82
4958	14:00:00	15:40:00	2024-12-10	21	82
4959	15:50:00	17:30:00	2024-08-07	21	83
4960	15:50:00	17:30:00	2024-08-14	21	83
4961	15:50:00	17:30:00	2024-08-21	21	83
4962	15:50:00	17:30:00	2024-08-28	21	83
4963	15:50:00	17:30:00	2024-09-04	21	83
4964	15:50:00	17:30:00	2024-09-11	21	83
4965	15:50:00	17:30:00	2024-09-18	21	83
4966	15:50:00	17:30:00	2024-09-25	21	83
4967	15:50:00	17:30:00	2024-10-02	21	83
4968	15:50:00	17:30:00	2024-10-09	21	83
4969	15:50:00	17:30:00	2024-10-16	21	83
4970	15:50:00	17:30:00	2024-10-23	21	83
4971	15:50:00	17:30:00	2024-10-30	21	83
4972	15:50:00	17:30:00	2024-11-06	21	83
4973	15:50:00	17:30:00	2024-11-13	21	83
4974	15:50:00	17:30:00	2024-11-20	21	83
4975	15:50:00	17:30:00	2024-11-27	21	83
4976	15:50:00	17:30:00	2024-12-04	21	83
4977	15:50:00	17:30:00	2024-12-11	21	83
3019	13:10:00	14:50:00	2024-08-05	11	404
3020	13:10:00	14:50:00	2024-08-12	11	404
3021	13:10:00	14:50:00	2024-08-19	11	404
3022	13:10:00	14:50:00	2024-08-26	11	404
3023	13:10:00	14:50:00	2024-09-02	11	404
3024	13:10:00	14:50:00	2024-09-09	11	404
3025	13:10:00	14:50:00	2024-09-16	11	404
3026	13:10:00	14:50:00	2024-09-23	11	404
3027	13:10:00	14:50:00	2024-09-30	11	404
3028	13:10:00	14:50:00	2024-10-07	11	404
3029	13:10:00	14:50:00	2024-10-14	11	404
3030	13:10:00	14:50:00	2024-10-21	11	404
3031	13:10:00	14:50:00	2024-10-28	11	404
3032	13:10:00	14:50:00	2024-11-04	11	404
3033	13:10:00	14:50:00	2024-11-11	11	404
3034	13:10:00	14:50:00	2024-11-18	11	404
3035	13:10:00	14:50:00	2024-11-25	11	404
3036	13:10:00	14:50:00	2024-12-02	11	404
3037	13:10:00	14:50:00	2024-12-09	11	404
3038	09:20:00	11:00:00	2024-08-08	11	405
3039	09:20:00	11:00:00	2024-08-15	11	405
3040	09:20:00	11:00:00	2024-08-22	11	405
3041	09:20:00	11:00:00	2024-08-29	11	405
3042	09:20:00	11:00:00	2024-09-05	11	405
3043	09:20:00	11:00:00	2024-09-12	11	405
3044	09:20:00	11:00:00	2024-09-19	11	405
3045	09:20:00	11:00:00	2024-09-26	11	405
3046	09:20:00	11:00:00	2024-10-03	11	405
3047	09:20:00	11:00:00	2024-10-10	11	405
3048	09:20:00	11:00:00	2024-10-17	11	405
3049	09:20:00	11:00:00	2024-10-24	11	405
3050	09:20:00	11:00:00	2024-10-31	11	405
3051	09:20:00	11:00:00	2024-11-07	11	405
3052	09:20:00	11:00:00	2024-11-14	11	405
3053	09:20:00	11:00:00	2024-11-21	11	405
3054	09:20:00	11:00:00	2024-11-28	11	405
3055	09:20:00	11:00:00	2024-12-05	11	405
3056	09:20:00	11:00:00	2024-12-12	11	405
3057	13:10:00	14:50:00	2024-08-05	10	406
3058	13:10:00	14:50:00	2024-08-12	10	406
3059	13:10:00	14:50:00	2024-08-19	10	406
3060	13:10:00	14:50:00	2024-08-26	10	406
3061	13:10:00	14:50:00	2024-09-02	10	406
3062	13:10:00	14:50:00	2024-09-09	10	406
3063	13:10:00	14:50:00	2024-09-16	10	406
3064	13:10:00	14:50:00	2024-09-23	10	406
3065	13:10:00	14:50:00	2024-09-30	10	406
3066	13:10:00	14:50:00	2024-10-07	10	406
3067	13:10:00	14:50:00	2024-10-14	10	406
3068	13:10:00	14:50:00	2024-10-21	10	406
3069	13:10:00	14:50:00	2024-10-28	10	406
3070	13:10:00	14:50:00	2024-11-04	10	406
3071	13:10:00	14:50:00	2024-11-11	10	406
3072	13:10:00	14:50:00	2024-11-18	10	406
3073	13:10:00	14:50:00	2024-11-25	10	406
3074	13:10:00	14:50:00	2024-12-02	10	406
3075	13:10:00	14:50:00	2024-12-09	10	406
3076	09:20:00	11:00:00	2024-08-08	10	407
3077	09:20:00	11:00:00	2024-08-15	10	407
3078	09:20:00	11:00:00	2024-08-22	10	407
3079	09:20:00	11:00:00	2024-08-29	10	407
3080	09:20:00	11:00:00	2024-09-05	10	407
3081	09:20:00	11:00:00	2024-09-12	10	407
3082	09:20:00	11:00:00	2024-09-19	10	407
3083	09:20:00	11:00:00	2024-09-26	10	407
3084	09:20:00	11:00:00	2024-10-03	10	407
3085	09:20:00	11:00:00	2024-10-10	10	407
3086	09:20:00	11:00:00	2024-10-17	10	407
3087	09:20:00	11:00:00	2024-10-24	10	407
3088	09:20:00	11:00:00	2024-10-31	10	407
3089	09:20:00	11:00:00	2024-11-07	10	407
3090	09:20:00	11:00:00	2024-11-14	10	407
3091	09:20:00	11:00:00	2024-11-21	10	407
3092	09:20:00	11:00:00	2024-11-28	10	407
3093	09:20:00	11:00:00	2024-12-05	10	407
3094	09:20:00	11:00:00	2024-12-12	10	407
3095	13:10:00	14:50:00	2024-08-05	13	408
3096	13:10:00	14:50:00	2024-08-12	13	408
3097	13:10:00	14:50:00	2024-08-19	13	408
3098	13:10:00	14:50:00	2024-08-26	13	408
3099	13:10:00	14:50:00	2024-09-02	13	408
3100	13:10:00	14:50:00	2024-09-09	13	408
3101	13:10:00	14:50:00	2024-09-16	13	408
3102	13:10:00	14:50:00	2024-09-23	13	408
3103	13:10:00	14:50:00	2024-09-30	13	408
3104	13:10:00	14:50:00	2024-10-07	13	408
3105	13:10:00	14:50:00	2024-10-14	13	408
3106	13:10:00	14:50:00	2024-10-21	13	408
3107	13:10:00	14:50:00	2024-10-28	13	408
3108	13:10:00	14:50:00	2024-11-04	13	408
3109	13:10:00	14:50:00	2024-11-11	13	408
3110	13:10:00	14:50:00	2024-11-18	13	408
3111	13:10:00	14:50:00	2024-11-25	13	408
3112	13:10:00	14:50:00	2024-12-02	13	408
3113	13:10:00	14:50:00	2024-12-09	13	408
3114	09:20:00	11:00:00	2024-08-08	13	409
3115	09:20:00	11:00:00	2024-08-15	13	409
3116	09:20:00	11:00:00	2024-08-22	13	409
3117	09:20:00	11:00:00	2024-08-29	13	409
3118	09:20:00	11:00:00	2024-09-05	13	409
3119	09:20:00	11:00:00	2024-09-12	13	409
3120	09:20:00	11:00:00	2024-09-19	13	409
3121	09:20:00	11:00:00	2024-09-26	13	409
3122	09:20:00	11:00:00	2024-10-03	13	409
3123	09:20:00	11:00:00	2024-10-10	13	409
3124	09:20:00	11:00:00	2024-10-17	13	409
3125	09:20:00	11:00:00	2024-10-24	13	409
3126	09:20:00	11:00:00	2024-10-31	13	409
3127	09:20:00	11:00:00	2024-11-07	13	409
3128	09:20:00	11:00:00	2024-11-14	13	409
3129	09:20:00	11:00:00	2024-11-21	13	409
3130	09:20:00	11:00:00	2024-11-28	13	409
3131	09:20:00	11:00:00	2024-12-05	13	409
3132	09:20:00	11:00:00	2024-12-12	13	409
3133	15:00:00	16:40:00	2024-08-05	12	410
3134	15:00:00	16:40:00	2024-08-12	12	410
3135	15:00:00	16:40:00	2024-08-19	12	410
3136	15:00:00	16:40:00	2024-08-26	12	410
3137	15:00:00	16:40:00	2024-09-02	12	410
3138	15:00:00	16:40:00	2024-09-09	12	410
3139	15:00:00	16:40:00	2024-09-16	12	410
3140	15:00:00	16:40:00	2024-09-23	12	410
3141	15:00:00	16:40:00	2024-09-30	12	410
3142	15:00:00	16:40:00	2024-10-07	12	410
3143	15:00:00	16:40:00	2024-10-14	12	410
3144	15:00:00	16:40:00	2024-10-21	12	410
3145	15:00:00	16:40:00	2024-10-28	12	410
3146	15:00:00	16:40:00	2024-11-04	12	410
3147	15:00:00	16:40:00	2024-11-11	12	410
3148	15:00:00	16:40:00	2024-11-18	12	410
3149	15:00:00	16:40:00	2024-11-25	12	410
3150	15:00:00	16:40:00	2024-12-02	12	410
3151	15:00:00	16:40:00	2024-12-09	12	410
3152	09:20:00	11:00:00	2024-08-08	12	411
3153	09:20:00	11:00:00	2024-08-15	12	411
3154	09:20:00	11:00:00	2024-08-22	12	411
3155	09:20:00	11:00:00	2024-08-29	12	411
3156	09:20:00	11:00:00	2024-09-05	12	411
3157	09:20:00	11:00:00	2024-09-12	12	411
3158	09:20:00	11:00:00	2024-09-19	12	411
3159	09:20:00	11:00:00	2024-09-26	12	411
3160	09:20:00	11:00:00	2024-10-03	12	411
3161	09:20:00	11:00:00	2024-10-10	12	411
3162	09:20:00	11:00:00	2024-10-17	12	411
3163	09:20:00	11:00:00	2024-10-24	12	411
3164	09:20:00	11:00:00	2024-10-31	12	411
3165	09:20:00	11:00:00	2024-11-07	12	411
3166	09:20:00	11:00:00	2024-11-14	12	411
3167	09:20:00	11:00:00	2024-11-21	12	411
3168	09:20:00	11:00:00	2024-11-28	12	411
3169	09:20:00	11:00:00	2024-12-05	12	411
3170	09:20:00	11:00:00	2024-12-12	12	411
4978	09:20:00	10:10:00	2024-08-10	68	84
4979	09:20:00	10:10:00	2024-08-17	68	84
4980	09:20:00	10:10:00	2024-08-24	68	84
4981	09:20:00	10:10:00	2024-08-31	68	84
4982	09:20:00	10:10:00	2024-09-07	68	84
4983	09:20:00	10:10:00	2024-09-14	68	84
4984	09:20:00	10:10:00	2024-09-21	68	84
4985	09:20:00	10:10:00	2024-09-28	68	84
4986	09:20:00	10:10:00	2024-10-05	68	84
4987	09:20:00	10:10:00	2024-10-12	68	84
4988	09:20:00	10:10:00	2024-10-19	68	84
4989	09:20:00	10:10:00	2024-10-26	68	84
4990	09:20:00	10:10:00	2024-11-02	68	84
4991	09:20:00	10:10:00	2024-11-09	68	84
4992	09:20:00	10:10:00	2024-11-16	68	84
4993	09:20:00	10:10:00	2024-11-23	68	84
4994	09:20:00	10:10:00	2024-11-30	68	84
4995	09:20:00	10:10:00	2024-12-07	68	84
4996	10:20:00	11:10:00	2024-08-10	68	85
4997	10:20:00	11:10:00	2024-08-17	68	85
4998	10:20:00	11:10:00	2024-08-24	68	85
4999	10:20:00	11:10:00	2024-08-31	68	85
5000	10:20:00	11:10:00	2024-09-07	68	85
5001	10:20:00	11:10:00	2024-09-14	68	85
5002	10:20:00	11:10:00	2024-09-21	68	85
5003	10:20:00	11:10:00	2024-09-28	68	85
5004	10:20:00	11:10:00	2024-10-05	68	85
5005	10:20:00	11:10:00	2024-10-12	68	85
5006	10:20:00	11:10:00	2024-10-19	68	85
5007	10:20:00	11:10:00	2024-10-26	68	85
5008	10:20:00	11:10:00	2024-11-02	68	85
5009	10:20:00	11:10:00	2024-11-09	68	85
5010	10:20:00	11:10:00	2024-11-16	68	85
5011	10:20:00	11:10:00	2024-11-23	68	85
5012	10:20:00	11:10:00	2024-11-30	68	85
5013	10:20:00	11:10:00	2024-12-07	68	85
5014	10:20:00	11:10:00	2024-08-10	68	87
5015	10:20:00	11:10:00	2024-08-17	68	87
5016	10:20:00	11:10:00	2024-08-24	68	87
5017	10:20:00	11:10:00	2024-08-31	68	87
5018	10:20:00	11:10:00	2024-09-07	68	87
5019	10:20:00	11:10:00	2024-09-14	68	87
5020	10:20:00	11:10:00	2024-09-21	68	87
5021	10:20:00	11:10:00	2024-09-28	68	87
5022	10:20:00	11:10:00	2024-10-05	68	87
5023	10:20:00	11:10:00	2024-10-12	68	87
5024	10:20:00	11:10:00	2024-10-19	68	87
5025	10:20:00	11:10:00	2024-10-26	68	87
5026	10:20:00	11:10:00	2024-11-02	68	87
5027	10:20:00	11:10:00	2024-11-09	68	87
5028	10:20:00	11:10:00	2024-11-16	68	87
5029	10:20:00	11:10:00	2024-11-23	68	87
5030	10:20:00	11:10:00	2024-11-30	68	87
5031	10:20:00	11:10:00	2024-12-07	68	87
5032	10:20:00	11:10:00	2024-08-10	68	86
5033	10:20:00	11:10:00	2024-08-17	68	86
5034	10:20:00	11:10:00	2024-08-24	68	86
5035	10:20:00	11:10:00	2024-08-31	68	86
5036	10:20:00	11:10:00	2024-09-07	68	86
5037	10:20:00	11:10:00	2024-09-14	68	86
5038	10:20:00	11:10:00	2024-09-21	68	86
5039	10:20:00	11:10:00	2024-09-28	68	86
5040	10:20:00	11:10:00	2024-10-05	68	86
5041	10:20:00	11:10:00	2024-10-12	68	86
5042	10:20:00	11:10:00	2024-10-19	68	86
5043	10:20:00	11:10:00	2024-10-26	68	86
5044	10:20:00	11:10:00	2024-11-02	68	86
5045	10:20:00	11:10:00	2024-11-09	68	86
5046	10:20:00	11:10:00	2024-11-16	68	86
5047	10:20:00	11:10:00	2024-11-23	68	86
5048	10:20:00	11:10:00	2024-11-30	68	86
5049	10:20:00	11:10:00	2024-12-07	68	86
5050	08:30:00	12:00:00	2024-08-09	72	88
5051	08:30:00	12:00:00	2024-08-16	72	88
5052	08:30:00	12:00:00	2024-08-23	72	88
5053	08:30:00	12:00:00	2024-08-30	72	88
5054	08:30:00	12:00:00	2024-09-06	72	88
5055	08:30:00	12:00:00	2024-09-13	72	88
5056	08:30:00	12:00:00	2024-09-20	72	88
5057	08:30:00	12:00:00	2024-09-27	72	88
5058	08:30:00	12:00:00	2024-10-04	72	88
5059	08:30:00	12:00:00	2024-10-11	72	88
5060	08:30:00	12:00:00	2024-10-18	72	88
5061	08:30:00	12:00:00	2024-10-25	72	88
5062	08:30:00	12:00:00	2024-11-01	72	88
5063	08:30:00	12:00:00	2024-11-08	72	88
5064	08:30:00	12:00:00	2024-11-15	72	88
5065	08:30:00	12:00:00	2024-11-22	72	88
3171	15:00:00	16:40:00	2024-08-05	10	412
3172	15:00:00	16:40:00	2024-08-12	10	412
3173	15:00:00	16:40:00	2024-08-19	10	412
3174	15:00:00	16:40:00	2024-08-26	10	412
3175	15:00:00	16:40:00	2024-09-02	10	412
3176	15:00:00	16:40:00	2024-09-09	10	412
3177	15:00:00	16:40:00	2024-09-16	10	412
3178	15:00:00	16:40:00	2024-09-23	10	412
3179	15:00:00	16:40:00	2024-09-30	10	412
3180	15:00:00	16:40:00	2024-10-07	10	412
3181	15:00:00	16:40:00	2024-10-14	10	412
3182	15:00:00	16:40:00	2024-10-21	10	412
3183	15:00:00	16:40:00	2024-10-28	10	412
3184	15:00:00	16:40:00	2024-11-04	10	412
3185	15:00:00	16:40:00	2024-11-11	10	412
3186	15:00:00	16:40:00	2024-11-18	10	412
3187	15:00:00	16:40:00	2024-11-25	10	412
3188	15:00:00	16:40:00	2024-12-02	10	412
3189	15:00:00	16:40:00	2024-12-09	10	412
3190	13:10:00	14:50:00	2024-08-08	10	413
3191	13:10:00	14:50:00	2024-08-15	10	413
3192	13:10:00	14:50:00	2024-08-22	10	413
3193	13:10:00	14:50:00	2024-08-29	10	413
3194	13:10:00	14:50:00	2024-09-05	10	413
3195	13:10:00	14:50:00	2024-09-12	10	413
3196	13:10:00	14:50:00	2024-09-19	10	413
3197	13:10:00	14:50:00	2024-09-26	10	413
3198	13:10:00	14:50:00	2024-10-03	10	413
3199	13:10:00	14:50:00	2024-10-10	10	413
3200	13:10:00	14:50:00	2024-10-17	10	413
3201	13:10:00	14:50:00	2024-10-24	10	413
3202	13:10:00	14:50:00	2024-10-31	10	413
3203	13:10:00	14:50:00	2024-11-07	10	413
3204	13:10:00	14:50:00	2024-11-14	10	413
3205	13:10:00	14:50:00	2024-11-21	10	413
3206	13:10:00	14:50:00	2024-11-28	10	413
3207	13:10:00	14:50:00	2024-12-05	10	413
3208	13:10:00	14:50:00	2024-12-12	10	413
3209	15:00:00	16:40:00	2024-08-05	11	414
3210	15:00:00	16:40:00	2024-08-12	11	414
3211	15:00:00	16:40:00	2024-08-19	11	414
3212	15:00:00	16:40:00	2024-08-26	11	414
3213	15:00:00	16:40:00	2024-09-02	11	414
3214	15:00:00	16:40:00	2024-09-09	11	414
3215	15:00:00	16:40:00	2024-09-16	11	414
3216	15:00:00	16:40:00	2024-09-23	11	414
3217	15:00:00	16:40:00	2024-09-30	11	414
3218	15:00:00	16:40:00	2024-10-07	11	414
3219	15:00:00	16:40:00	2024-10-14	11	414
3220	15:00:00	16:40:00	2024-10-21	11	414
3221	15:00:00	16:40:00	2024-10-28	11	414
3222	15:00:00	16:40:00	2024-11-04	11	414
3223	15:00:00	16:40:00	2024-11-11	11	414
3224	15:00:00	16:40:00	2024-11-18	11	414
3225	15:00:00	16:40:00	2024-11-25	11	414
3226	15:00:00	16:40:00	2024-12-02	11	414
3227	15:00:00	16:40:00	2024-12-09	11	414
3228	13:10:00	14:50:00	2024-08-07	11	415
3229	13:10:00	14:50:00	2024-08-14	11	415
3230	13:10:00	14:50:00	2024-08-21	11	415
3231	13:10:00	14:50:00	2024-08-28	11	415
3232	13:10:00	14:50:00	2024-09-04	11	415
3233	13:10:00	14:50:00	2024-09-11	11	415
3234	13:10:00	14:50:00	2024-09-18	11	415
3235	13:10:00	14:50:00	2024-09-25	11	415
3236	13:10:00	14:50:00	2024-10-02	11	415
3237	13:10:00	14:50:00	2024-10-09	11	415
3238	13:10:00	14:50:00	2024-10-16	11	415
3239	13:10:00	14:50:00	2024-10-23	11	415
3240	13:10:00	14:50:00	2024-10-30	11	415
3241	13:10:00	14:50:00	2024-11-06	11	415
3242	13:10:00	14:50:00	2024-11-13	11	415
3243	13:10:00	14:50:00	2024-11-20	11	415
3244	13:10:00	14:50:00	2024-11-27	11	415
3245	13:10:00	14:50:00	2024-12-04	11	415
3246	13:10:00	14:50:00	2024-12-11	11	415
3247	15:00:00	16:40:00	2024-08-05	71	416
3248	15:00:00	16:40:00	2024-08-12	71	416
3249	15:00:00	16:40:00	2024-08-19	71	416
3250	15:00:00	16:40:00	2024-08-26	71	416
3251	15:00:00	16:40:00	2024-09-02	71	416
3252	15:00:00	16:40:00	2024-09-09	71	416
3253	15:00:00	16:40:00	2024-09-16	71	416
3254	15:00:00	16:40:00	2024-09-23	71	416
3255	15:00:00	16:40:00	2024-09-30	71	416
3256	15:00:00	16:40:00	2024-10-07	71	416
3257	15:00:00	16:40:00	2024-10-14	71	416
3258	15:00:00	16:40:00	2024-10-21	71	416
3259	15:00:00	16:40:00	2024-10-28	71	416
3260	15:00:00	16:40:00	2024-11-04	71	416
3261	15:00:00	16:40:00	2024-11-11	71	416
3262	15:00:00	16:40:00	2024-11-18	71	416
3263	15:00:00	16:40:00	2024-11-25	71	416
3264	15:00:00	16:40:00	2024-12-02	71	416
3265	15:00:00	16:40:00	2024-12-09	71	416
3266	15:00:00	16:40:00	2024-08-05	70	417
3267	15:00:00	16:40:00	2024-08-12	70	417
3268	15:00:00	16:40:00	2024-08-19	70	417
3269	15:00:00	16:40:00	2024-08-26	70	417
3270	15:00:00	16:40:00	2024-09-02	70	417
3271	15:00:00	16:40:00	2024-09-09	70	417
3272	15:00:00	16:40:00	2024-09-16	70	417
3273	15:00:00	16:40:00	2024-09-23	70	417
3274	15:00:00	16:40:00	2024-09-30	70	417
3275	15:00:00	16:40:00	2024-10-07	70	417
3276	15:00:00	16:40:00	2024-10-14	70	417
3277	15:00:00	16:40:00	2024-10-21	70	417
3278	15:00:00	16:40:00	2024-10-28	70	417
3279	15:00:00	16:40:00	2024-11-04	70	417
3280	15:00:00	16:40:00	2024-11-11	70	417
3281	15:00:00	16:40:00	2024-11-18	70	417
3282	15:00:00	16:40:00	2024-11-25	70	417
3283	15:00:00	16:40:00	2024-12-02	70	417
3284	15:00:00	16:40:00	2024-12-09	70	417
3285	13:10:00	14:50:00	2024-08-05	71	418
3286	13:10:00	14:50:00	2024-08-12	71	418
3287	13:10:00	14:50:00	2024-08-19	71	418
3288	13:10:00	14:50:00	2024-08-26	71	418
3289	13:10:00	14:50:00	2024-09-02	71	418
3290	13:10:00	14:50:00	2024-09-09	71	418
3291	13:10:00	14:50:00	2024-09-16	71	418
3292	13:10:00	14:50:00	2024-09-23	71	418
3293	13:10:00	14:50:00	2024-09-30	71	418
3294	13:10:00	14:50:00	2024-10-07	71	418
3295	13:10:00	14:50:00	2024-10-14	71	418
3296	13:10:00	14:50:00	2024-10-21	71	418
3297	13:10:00	14:50:00	2024-10-28	71	418
3298	13:10:00	14:50:00	2024-11-04	71	418
3299	13:10:00	14:50:00	2024-11-11	71	418
3300	13:10:00	14:50:00	2024-11-18	71	418
3301	13:10:00	14:50:00	2024-11-25	71	418
3302	13:10:00	14:50:00	2024-12-02	71	418
3303	13:10:00	14:50:00	2024-12-09	71	418
5066	08:30:00	12:00:00	2024-11-29	72	88
5067	08:30:00	12:00:00	2024-12-06	72	88
5068	09:10:00	12:10:00	2024-08-07	21	89
5069	09:10:00	12:10:00	2024-08-14	21	89
5070	09:10:00	12:10:00	2024-08-21	21	89
5071	09:10:00	12:10:00	2024-08-28	21	89
5072	09:10:00	12:10:00	2024-09-04	21	89
5073	09:10:00	12:10:00	2024-09-11	21	89
5074	09:10:00	12:10:00	2024-09-18	21	89
5075	09:10:00	12:10:00	2024-09-25	21	89
5076	09:10:00	12:10:00	2024-10-02	21	89
5077	09:10:00	12:10:00	2024-10-09	21	89
5078	09:10:00	12:10:00	2024-10-16	21	89
5079	09:10:00	12:10:00	2024-10-23	21	89
5080	09:10:00	12:10:00	2024-10-30	21	89
5081	09:10:00	12:10:00	2024-11-06	21	89
5082	09:10:00	12:10:00	2024-11-13	21	89
5083	09:10:00	12:10:00	2024-11-20	21	89
5084	09:10:00	12:10:00	2024-11-27	21	89
5085	09:10:00	12:10:00	2024-12-04	21	89
5086	09:10:00	12:10:00	2024-12-11	21	89
5703	09:20:00	11:00:00	2024-09-11	22	140
5704	09:20:00	11:00:00	2024-09-18	22	140
5705	09:20:00	11:00:00	2024-09-25	22	140
5706	09:20:00	11:00:00	2024-10-02	22	140
5707	09:20:00	11:00:00	2024-10-09	22	140
5708	09:20:00	11:00:00	2024-10-16	22	140
5709	09:20:00	11:00:00	2024-10-23	22	140
5710	09:20:00	11:00:00	2024-10-30	22	140
5711	09:20:00	11:00:00	2024-11-06	22	140
5712	09:20:00	11:00:00	2024-11-13	22	140
5713	09:20:00	11:00:00	2024-11-20	22	140
5714	09:20:00	11:00:00	2024-11-27	22	140
5715	09:20:00	11:00:00	2024-12-04	22	140
5716	09:20:00	11:00:00	2024-12-11	22	140
5829	09:20:00	11:00:00	2024-08-06	65	148
5830	09:20:00	11:00:00	2024-08-13	65	148
5831	09:20:00	11:00:00	2024-08-20	65	148
5832	09:20:00	11:00:00	2024-08-27	65	148
5833	09:20:00	11:00:00	2024-09-03	65	148
5834	09:20:00	11:00:00	2024-09-10	65	148
5835	09:20:00	11:00:00	2024-09-17	65	148
5836	09:20:00	11:00:00	2024-09-24	65	148
5837	09:20:00	11:00:00	2024-10-01	65	148
5838	09:20:00	11:00:00	2024-10-08	65	148
5839	09:20:00	11:00:00	2024-10-15	65	148
5840	09:20:00	11:00:00	2024-10-22	65	148
5841	09:20:00	11:00:00	2024-10-29	65	148
5842	09:20:00	11:00:00	2024-11-05	65	148
5843	09:20:00	11:00:00	2024-11-12	65	148
5844	09:20:00	11:00:00	2024-11-19	65	148
5845	09:20:00	11:00:00	2024-11-26	65	148
5846	09:20:00	11:00:00	2024-12-03	65	148
5847	09:20:00	11:00:00	2024-12-10	65	148
5848	07:30:00	09:10:00	2024-08-08	26	149
5849	07:30:00	09:10:00	2024-08-15	26	149
5850	07:30:00	09:10:00	2024-08-22	26	149
5851	07:30:00	09:10:00	2024-08-29	26	149
5852	07:30:00	09:10:00	2024-09-05	26	149
5853	07:30:00	09:10:00	2024-09-12	26	149
5854	07:30:00	09:10:00	2024-09-19	26	149
5855	07:30:00	09:10:00	2024-09-26	26	149
5856	07:30:00	09:10:00	2024-10-03	26	149
5857	07:30:00	09:10:00	2024-10-10	26	149
5858	07:30:00	09:10:00	2024-10-17	26	149
5859	07:30:00	09:10:00	2024-10-24	26	149
5860	07:30:00	09:10:00	2024-10-31	26	149
5861	07:30:00	09:10:00	2024-11-07	26	149
5862	07:30:00	09:10:00	2024-11-14	26	149
3491	13:10:00	14:50:00	2024-08-06	18	450
3492	13:10:00	14:50:00	2024-08-13	18	450
3493	13:10:00	14:50:00	2024-08-20	18	450
3494	13:10:00	14:50:00	2024-08-27	18	450
3495	13:10:00	14:50:00	2024-09-03	18	450
3496	13:10:00	14:50:00	2024-09-10	18	450
3497	13:10:00	14:50:00	2024-09-17	18	450
3498	13:10:00	14:50:00	2024-09-24	18	450
3499	13:10:00	14:50:00	2024-10-01	18	450
3500	13:10:00	14:50:00	2024-10-08	18	450
3501	13:10:00	14:50:00	2024-10-15	18	450
3502	13:10:00	14:50:00	2024-10-22	18	450
3503	13:10:00	14:50:00	2024-10-29	18	450
3504	13:10:00	14:50:00	2024-11-05	18	450
3505	13:10:00	14:50:00	2024-11-12	18	450
3506	13:10:00	14:50:00	2024-11-19	18	450
3507	13:10:00	14:50:00	2024-11-26	18	450
3508	13:10:00	14:50:00	2024-12-03	18	450
3509	13:10:00	14:50:00	2024-12-10	18	450
3510	09:20:00	11:00:00	2024-08-09	18	451
3511	09:20:00	11:00:00	2024-08-16	18	451
3512	09:20:00	11:00:00	2024-08-23	18	451
3513	09:20:00	11:00:00	2024-08-30	18	451
3514	09:20:00	11:00:00	2024-09-06	18	451
3515	09:20:00	11:00:00	2024-09-13	18	451
3516	09:20:00	11:00:00	2024-09-20	18	451
3517	09:20:00	11:00:00	2024-09-27	18	451
3518	09:20:00	11:00:00	2024-10-04	18	451
3519	09:20:00	11:00:00	2024-10-11	18	451
3520	09:20:00	11:00:00	2024-10-18	18	451
3521	09:20:00	11:00:00	2024-10-25	18	451
3522	09:20:00	11:00:00	2024-11-01	18	451
3523	09:20:00	11:00:00	2024-11-08	18	451
3524	09:20:00	11:00:00	2024-11-15	18	451
3525	09:20:00	11:00:00	2024-11-22	18	451
5112	08:20:00	10:00:00	2024-07-18	23	91
5113	08:20:00	10:00:00	2024-07-25	23	91
5114	08:20:00	10:00:00	2024-08-01	23	91
5115	08:20:00	10:00:00	2024-08-08	23	91
5116	08:20:00	10:00:00	2024-08-15	23	91
5117	16:50:00	18:30:00	2024-08-06	22	92
5118	16:50:00	18:30:00	2024-08-13	22	92
5119	16:50:00	18:30:00	2024-08-20	22	92
5120	16:50:00	18:30:00	2024-08-27	22	92
5121	16:50:00	18:30:00	2024-09-03	22	92
5122	16:50:00	18:30:00	2024-09-10	22	92
5123	16:50:00	18:30:00	2024-09-17	22	92
5124	16:50:00	18:30:00	2024-09-24	22	92
5125	16:50:00	18:30:00	2024-10-01	22	92
5126	16:50:00	18:30:00	2024-10-08	22	92
5127	16:50:00	18:30:00	2024-10-15	22	92
5128	16:50:00	18:30:00	2024-10-22	22	92
5129	16:50:00	18:30:00	2024-10-29	22	92
5130	16:50:00	18:30:00	2024-11-05	22	92
5131	16:50:00	18:30:00	2024-11-12	22	92
5132	16:50:00	18:30:00	2024-11-19	22	92
5133	16:50:00	18:30:00	2024-11-26	22	92
5134	16:50:00	18:30:00	2024-12-03	22	92
5135	16:50:00	18:30:00	2024-12-10	22	92
5717	18:00:00	19:40:00	2024-08-05	24	141
5718	18:00:00	19:40:00	2024-08-12	24	141
5719	18:00:00	19:40:00	2024-08-19	24	141
5720	18:00:00	19:40:00	2024-08-26	24	141
5721	18:00:00	19:40:00	2024-09-02	24	141
5722	18:00:00	19:40:00	2024-09-09	24	141
5723	18:00:00	19:40:00	2024-09-16	24	141
5724	18:00:00	19:40:00	2024-09-23	24	141
5725	18:00:00	19:40:00	2024-09-30	24	141
5726	18:00:00	19:40:00	2024-10-07	24	141
5727	18:00:00	19:40:00	2024-10-14	24	141
5728	18:00:00	19:40:00	2024-10-21	24	141
5729	18:00:00	19:40:00	2024-10-28	24	141
5730	18:00:00	19:40:00	2024-11-04	24	141
5731	18:00:00	19:40:00	2024-11-11	24	141
5732	18:00:00	19:40:00	2024-11-18	24	141
5733	18:00:00	19:40:00	2024-11-25	24	141
5734	18:00:00	19:40:00	2024-12-02	24	141
5735	18:00:00	19:40:00	2024-12-09	24	141
5736	18:00:00	19:40:00	2024-08-07	24	142
5737	18:00:00	19:40:00	2024-08-14	24	142
5738	18:00:00	19:40:00	2024-08-21	24	142
5739	18:00:00	19:40:00	2024-08-28	24	142
5740	18:00:00	19:40:00	2024-09-04	24	142
5741	18:00:00	19:40:00	2024-09-11	24	142
5742	18:00:00	19:40:00	2024-09-18	24	142
5743	18:00:00	19:40:00	2024-09-25	24	142
5744	18:00:00	19:40:00	2024-10-02	24	142
5745	18:00:00	19:40:00	2024-10-09	24	142
5746	18:00:00	19:40:00	2024-10-16	24	142
5747	18:00:00	19:40:00	2024-10-23	24	142
5748	18:00:00	19:40:00	2024-10-30	24	142
5749	18:00:00	19:40:00	2024-11-06	24	142
5750	18:00:00	19:40:00	2024-11-13	24	142
5751	18:00:00	19:40:00	2024-11-20	24	142
5752	18:00:00	19:40:00	2024-11-27	24	142
5753	18:00:00	19:40:00	2024-12-04	24	142
5754	18:00:00	19:40:00	2024-12-11	24	142
5810	09:20:00	12:50:00	2024-08-07	65	147
5811	09:20:00	12:50:00	2024-08-14	65	147
5812	09:20:00	12:50:00	2024-08-21	65	147
5813	09:20:00	12:50:00	2024-08-28	65	147
5814	09:20:00	12:50:00	2024-09-04	65	147
5815	09:20:00	12:50:00	2024-09-11	65	147
5816	09:20:00	12:50:00	2024-09-18	65	147
5817	09:20:00	12:50:00	2024-09-25	65	147
5818	09:20:00	12:50:00	2024-10-02	65	147
5819	09:20:00	12:50:00	2024-10-09	65	147
5820	09:20:00	12:50:00	2024-10-16	65	147
5821	09:20:00	12:50:00	2024-10-23	65	147
5822	09:20:00	12:50:00	2024-10-30	65	147
5823	09:20:00	12:50:00	2024-11-06	65	147
5824	09:20:00	12:50:00	2024-11-13	65	147
5825	09:20:00	12:50:00	2024-11-20	65	147
5826	09:20:00	12:50:00	2024-11-27	65	147
5827	09:20:00	12:50:00	2024-12-04	65	147
5828	09:20:00	12:50:00	2024-12-11	65	147
5867	07:30:00	09:10:00	2024-08-05	26	150
5868	07:30:00	09:10:00	2024-08-12	26	150
5869	07:30:00	09:10:00	2024-08-19	26	150
5870	07:30:00	09:10:00	2024-08-26	26	150
5871	07:30:00	09:10:00	2024-09-02	26	150
5872	07:30:00	09:10:00	2024-09-09	26	150
5873	07:30:00	09:10:00	2024-09-16	26	150
5874	07:30:00	09:10:00	2024-09-23	26	150
5875	07:30:00	09:10:00	2024-09-30	26	150
5876	07:30:00	09:10:00	2024-10-07	26	150
5877	07:30:00	09:10:00	2024-10-14	26	150
5878	07:30:00	09:10:00	2024-10-21	26	150
5879	07:30:00	09:10:00	2024-10-28	26	150
5880	07:30:00	09:10:00	2024-11-04	26	150
5881	07:30:00	09:10:00	2024-11-11	26	150
5882	07:30:00	09:10:00	2024-11-18	26	150
5883	07:30:00	09:10:00	2024-11-25	26	150
5884	07:30:00	09:10:00	2024-12-02	26	150
5885	07:30:00	09:10:00	2024-12-09	26	150
5886	09:20:00	11:00:00	2024-08-09	26	151
5887	09:20:00	11:00:00	2024-08-16	26	151
5888	09:20:00	11:00:00	2024-08-23	26	151
5889	09:20:00	11:00:00	2024-08-30	26	151
5890	09:20:00	11:00:00	2024-09-06	26	151
5891	09:20:00	11:00:00	2024-09-13	26	151
5892	09:20:00	11:00:00	2024-09-20	26	151
5893	09:20:00	11:00:00	2024-09-27	26	151
5894	09:20:00	11:00:00	2024-10-04	26	151
5895	09:20:00	11:00:00	2024-10-11	26	151
5896	09:20:00	11:00:00	2024-10-18	26	151
5897	09:20:00	11:00:00	2024-10-25	26	151
5898	09:20:00	11:00:00	2024-11-01	26	151
5899	09:20:00	11:00:00	2024-11-08	26	151
5900	09:20:00	11:00:00	2024-11-15	26	151
5901	09:20:00	11:00:00	2024-11-22	26	151
5902	09:20:00	11:00:00	2024-11-29	26	151
5903	09:20:00	11:00:00	2024-12-06	26	151
5904	09:20:00	12:50:00	2024-08-08	39	152
5905	09:20:00	12:50:00	2024-08-15	39	152
3526	09:20:00	11:00:00	2024-11-29	18	451
3527	09:20:00	11:00:00	2024-12-06	18	451
3565	07:30:00	09:10:00	2024-08-06	16	448
3566	07:30:00	09:10:00	2024-08-13	16	448
3567	07:30:00	09:10:00	2024-08-20	16	448
3568	07:30:00	09:10:00	2024-08-27	16	448
3569	07:30:00	09:10:00	2024-09-03	16	448
3570	07:30:00	09:10:00	2024-09-10	16	448
3571	07:30:00	09:10:00	2024-09-17	16	448
3572	07:30:00	09:10:00	2024-09-24	16	448
3573	07:30:00	09:10:00	2024-10-01	16	448
3574	07:30:00	09:10:00	2024-10-08	16	448
3575	07:30:00	09:10:00	2024-10-15	16	448
3576	07:30:00	09:10:00	2024-10-22	16	448
3577	07:30:00	09:10:00	2024-10-29	16	448
3578	07:30:00	09:10:00	2024-11-05	16	448
3579	07:30:00	09:10:00	2024-11-12	16	448
3580	07:30:00	09:10:00	2024-11-19	16	448
3581	07:30:00	09:10:00	2024-11-26	16	448
3582	07:30:00	09:10:00	2024-12-03	16	448
3583	07:30:00	09:10:00	2024-12-10	16	448
3584	09:20:00	11:00:00	2024-08-09	16	449
3585	09:20:00	11:00:00	2024-08-16	16	449
3586	09:20:00	11:00:00	2024-08-23	16	449
3587	09:20:00	11:00:00	2024-08-30	16	449
3588	09:20:00	11:00:00	2024-09-06	16	449
3589	09:20:00	11:00:00	2024-09-13	16	449
3590	09:20:00	11:00:00	2024-09-20	16	449
3591	09:20:00	11:00:00	2024-09-27	16	449
3592	09:20:00	11:00:00	2024-10-04	16	449
3593	09:20:00	11:00:00	2024-10-11	16	449
3594	09:20:00	11:00:00	2024-10-18	16	449
3595	09:20:00	11:00:00	2024-10-25	16	449
3596	09:20:00	11:00:00	2024-11-01	16	449
3597	09:20:00	11:00:00	2024-11-08	16	449
3598	09:20:00	11:00:00	2024-11-15	16	449
3599	09:20:00	11:00:00	2024-11-22	16	449
3600	09:20:00	11:00:00	2024-11-29	16	449
3601	09:20:00	11:00:00	2024-12-06	16	449
5136	11:10:00	12:50:00	2024-08-07	38	98
5137	11:10:00	12:50:00	2024-08-14	38	98
5138	11:10:00	12:50:00	2024-08-21	38	98
5139	11:10:00	12:50:00	2024-08-28	38	98
5140	11:10:00	12:50:00	2024-09-04	38	98
5141	11:10:00	12:50:00	2024-09-11	38	98
5142	11:10:00	12:50:00	2024-09-18	38	98
5143	11:10:00	12:50:00	2024-09-25	38	98
5144	11:10:00	12:50:00	2024-10-02	38	98
5145	11:10:00	12:50:00	2024-10-09	38	98
5146	11:10:00	12:50:00	2024-10-16	38	98
5147	11:10:00	12:50:00	2024-10-23	38	98
5148	11:10:00	12:50:00	2024-10-30	38	98
5149	11:10:00	12:50:00	2024-11-06	38	98
5150	11:10:00	12:50:00	2024-11-13	38	98
5151	11:10:00	12:50:00	2024-11-20	38	98
5152	11:10:00	12:50:00	2024-11-27	38	98
5153	11:10:00	12:50:00	2024-12-04	38	98
5154	11:10:00	12:50:00	2024-12-11	38	98
5155	09:20:00	11:00:00	2024-08-09	38	99
5156	09:20:00	11:00:00	2024-08-16	38	99
5157	09:20:00	11:00:00	2024-08-23	38	99
5158	09:20:00	11:00:00	2024-08-30	38	99
5159	09:20:00	11:00:00	2024-09-06	38	99
5160	09:20:00	11:00:00	2024-09-13	38	99
5161	09:20:00	11:00:00	2024-09-20	38	99
5162	09:20:00	11:00:00	2024-09-27	38	99
5163	09:20:00	11:00:00	2024-10-04	38	99
5164	09:20:00	11:00:00	2024-10-11	38	99
5165	09:20:00	11:00:00	2024-10-18	38	99
5166	09:20:00	11:00:00	2024-10-25	38	99
5167	09:20:00	11:00:00	2024-11-01	38	99
5168	09:20:00	11:00:00	2024-11-08	38	99
5169	09:20:00	11:00:00	2024-11-15	38	99
5170	09:20:00	11:00:00	2024-11-22	38	99
5171	09:20:00	11:00:00	2024-11-29	38	99
5172	09:20:00	11:00:00	2024-12-06	38	99
5210	11:10:00	12:50:00	2024-08-07	33	102
5211	11:10:00	12:50:00	2024-08-14	33	102
5212	11:10:00	12:50:00	2024-08-21	33	102
5213	11:10:00	12:50:00	2024-08-28	33	102
5214	11:10:00	12:50:00	2024-09-04	33	102
5215	11:10:00	12:50:00	2024-09-11	33	102
5216	11:10:00	12:50:00	2024-09-18	33	102
5217	11:10:00	12:50:00	2024-09-25	33	102
5218	11:10:00	12:50:00	2024-10-02	33	102
5219	11:10:00	12:50:00	2024-10-09	33	102
5220	11:10:00	12:50:00	2024-10-16	33	102
5221	11:10:00	12:50:00	2024-10-23	33	102
5222	11:10:00	12:50:00	2024-10-30	33	102
5223	11:10:00	12:50:00	2024-11-06	33	102
5224	11:10:00	12:50:00	2024-11-13	33	102
5225	11:10:00	12:50:00	2024-11-20	33	102
5226	11:10:00	12:50:00	2024-11-27	33	102
5227	11:10:00	12:50:00	2024-12-04	33	102
5228	11:10:00	12:50:00	2024-12-11	33	102
5229	09:20:00	11:00:00	2024-08-09	33	103
5230	09:20:00	11:00:00	2024-08-16	33	103
5231	09:20:00	11:00:00	2024-08-23	33	103
5232	09:20:00	11:00:00	2024-08-30	33	103
5233	09:20:00	11:00:00	2024-09-06	33	103
5234	09:20:00	11:00:00	2024-09-13	33	103
5235	09:20:00	11:00:00	2024-09-20	33	103
5236	09:20:00	11:00:00	2024-09-27	33	103
5237	09:20:00	11:00:00	2024-10-04	33	103
5238	09:20:00	11:00:00	2024-10-11	33	103
5239	09:20:00	11:00:00	2024-10-18	33	103
5240	09:20:00	11:00:00	2024-10-25	33	103
5241	09:20:00	11:00:00	2024-11-01	33	103
5242	09:20:00	11:00:00	2024-11-08	33	103
5243	09:20:00	11:00:00	2024-11-15	33	103
5244	09:20:00	11:00:00	2024-11-22	33	103
5245	09:20:00	11:00:00	2024-11-29	33	103
5246	09:20:00	11:00:00	2024-12-06	33	103
5755	11:10:00	12:50:00	2024-08-09	32	144
5756	11:10:00	12:50:00	2024-08-16	32	144
5757	11:10:00	12:50:00	2024-08-23	32	144
5758	11:10:00	12:50:00	2024-08-30	32	144
5759	11:10:00	12:50:00	2024-09-06	32	144
5760	11:10:00	12:50:00	2024-09-13	32	144
5761	11:10:00	12:50:00	2024-09-20	32	144
3528	09:20:00	11:00:00	2024-08-06	17	446
3529	09:20:00	11:00:00	2024-08-13	17	446
3530	09:20:00	11:00:00	2024-08-20	17	446
3531	09:20:00	11:00:00	2024-08-27	17	446
3532	09:20:00	11:00:00	2024-09-03	17	446
3533	09:20:00	11:00:00	2024-09-10	17	446
3534	09:20:00	11:00:00	2024-09-17	17	446
3535	09:20:00	11:00:00	2024-09-24	17	446
3536	09:20:00	11:00:00	2024-10-01	17	446
3537	09:20:00	11:00:00	2024-10-08	17	446
3538	09:20:00	11:00:00	2024-10-15	17	446
3539	09:20:00	11:00:00	2024-10-22	17	446
3540	09:20:00	11:00:00	2024-10-29	17	446
3541	09:20:00	11:00:00	2024-11-05	17	446
3542	09:20:00	11:00:00	2024-11-12	17	446
3543	09:20:00	11:00:00	2024-11-19	17	446
3544	09:20:00	11:00:00	2024-11-26	17	446
3545	09:20:00	11:00:00	2024-12-03	17	446
3546	09:20:00	11:00:00	2024-12-10	17	446
3547	07:30:00	09:10:00	2024-08-09	17	447
3548	07:30:00	09:10:00	2024-08-16	17	447
3549	07:30:00	09:10:00	2024-08-23	17	447
3550	07:30:00	09:10:00	2024-08-30	17	447
3551	07:30:00	09:10:00	2024-09-06	17	447
3552	07:30:00	09:10:00	2024-09-13	17	447
3553	07:30:00	09:10:00	2024-09-20	17	447
3554	07:30:00	09:10:00	2024-09-27	17	447
3555	07:30:00	09:10:00	2024-10-04	17	447
3556	07:30:00	09:10:00	2024-10-11	17	447
3557	07:30:00	09:10:00	2024-10-18	17	447
3558	07:30:00	09:10:00	2024-10-25	17	447
3559	07:30:00	09:10:00	2024-11-01	17	447
3560	07:30:00	09:10:00	2024-11-08	17	447
3561	07:30:00	09:10:00	2024-11-15	17	447
3562	07:30:00	09:10:00	2024-11-22	17	447
3563	07:30:00	09:10:00	2024-11-29	17	447
3564	07:30:00	09:10:00	2024-12-06	17	447
3602	07:30:00	09:10:00	2024-08-05	16	432
3603	07:30:00	09:10:00	2024-08-12	16	432
3604	07:30:00	09:10:00	2024-08-19	16	432
3605	07:30:00	09:10:00	2024-08-26	16	432
3606	07:30:00	09:10:00	2024-09-02	16	432
3607	07:30:00	09:10:00	2024-09-09	16	432
3608	07:30:00	09:10:00	2024-09-16	16	432
3609	07:30:00	09:10:00	2024-09-23	16	432
3610	07:30:00	09:10:00	2024-09-30	16	432
3611	07:30:00	09:10:00	2024-10-07	16	432
3612	07:30:00	09:10:00	2024-10-14	16	432
3613	07:30:00	09:10:00	2024-10-21	16	432
3614	07:30:00	09:10:00	2024-10-28	16	432
3615	07:30:00	09:10:00	2024-11-04	16	432
3616	07:30:00	09:10:00	2024-11-11	16	432
3617	07:30:00	09:10:00	2024-11-18	16	432
3618	07:30:00	09:10:00	2024-11-25	16	432
3619	07:30:00	09:10:00	2024-12-02	16	432
3620	07:30:00	09:10:00	2024-12-09	16	432
3621	09:20:00	11:00:00	2024-08-08	16	433
3622	09:20:00	11:00:00	2024-08-15	16	433
3623	09:20:00	11:00:00	2024-08-22	16	433
3624	09:20:00	11:00:00	2024-08-29	16	433
3625	09:20:00	11:00:00	2024-09-05	16	433
3626	09:20:00	11:00:00	2024-09-12	16	433
3627	09:20:00	11:00:00	2024-09-19	16	433
3628	09:20:00	11:00:00	2024-09-26	16	433
3629	09:20:00	11:00:00	2024-10-03	16	433
3630	09:20:00	11:00:00	2024-10-10	16	433
3631	09:20:00	11:00:00	2024-10-17	16	433
3632	09:20:00	11:00:00	2024-10-24	16	433
3633	09:20:00	11:00:00	2024-10-31	16	433
3634	09:20:00	11:00:00	2024-11-07	16	433
3635	09:20:00	11:00:00	2024-11-14	16	433
3636	09:20:00	11:00:00	2024-11-21	16	433
3637	09:20:00	11:00:00	2024-11-28	16	433
3638	09:20:00	11:00:00	2024-12-05	16	433
3639	09:20:00	11:00:00	2024-12-12	16	433
3640	15:00:00	16:40:00	2024-08-05	16	434
3641	15:00:00	16:40:00	2024-08-12	16	434
3642	15:00:00	16:40:00	2024-08-19	16	434
3643	15:00:00	16:40:00	2024-08-26	16	434
3644	15:00:00	16:40:00	2024-09-02	16	434
3645	15:00:00	16:40:00	2024-09-09	16	434
3646	15:00:00	16:40:00	2024-09-16	16	434
3647	15:00:00	16:40:00	2024-09-23	16	434
3648	15:00:00	16:40:00	2024-09-30	16	434
3649	15:00:00	16:40:00	2024-10-07	16	434
3650	15:00:00	16:40:00	2024-10-14	16	434
3651	15:00:00	16:40:00	2024-10-21	16	434
3652	15:00:00	16:40:00	2024-10-28	16	434
3653	15:00:00	16:40:00	2024-11-04	16	434
3654	15:00:00	16:40:00	2024-11-11	16	434
3655	15:00:00	16:40:00	2024-11-18	16	434
3656	15:00:00	16:40:00	2024-11-25	16	434
3657	15:00:00	16:40:00	2024-12-02	16	434
3658	15:00:00	16:40:00	2024-12-09	16	434
3659	13:10:00	14:50:00	2024-08-08	16	435
3660	13:10:00	14:50:00	2024-08-15	16	435
3661	13:10:00	14:50:00	2024-08-22	16	435
3662	13:10:00	14:50:00	2024-08-29	16	435
3663	13:10:00	14:50:00	2024-09-05	16	435
3664	13:10:00	14:50:00	2024-09-12	16	435
3665	13:10:00	14:50:00	2024-09-19	16	435
3666	13:10:00	14:50:00	2024-09-26	16	435
3667	13:10:00	14:50:00	2024-10-03	16	435
3668	13:10:00	14:50:00	2024-10-10	16	435
3669	13:10:00	14:50:00	2024-10-17	16	435
3670	13:10:00	14:50:00	2024-10-24	16	435
3671	13:10:00	14:50:00	2024-10-31	16	435
3672	13:10:00	14:50:00	2024-11-07	16	435
3673	13:10:00	14:50:00	2024-11-14	16	435
3674	13:10:00	14:50:00	2024-11-21	16	435
3675	13:10:00	14:50:00	2024-11-28	16	435
3676	13:10:00	14:50:00	2024-12-05	16	435
3677	13:10:00	14:50:00	2024-12-12	16	435
3678	13:10:00	14:50:00	2024-08-05	17	436
3679	13:10:00	14:50:00	2024-08-12	17	436
3680	13:10:00	14:50:00	2024-08-19	17	436
3681	13:10:00	14:50:00	2024-08-26	17	436
3682	13:10:00	14:50:00	2024-09-02	17	436
3683	13:10:00	14:50:00	2024-09-09	17	436
3684	13:10:00	14:50:00	2024-09-16	17	436
3685	13:10:00	14:50:00	2024-09-23	17	436
3686	13:10:00	14:50:00	2024-09-30	17	436
3687	13:10:00	14:50:00	2024-10-07	17	436
3688	13:10:00	14:50:00	2024-10-14	17	436
3689	13:10:00	14:50:00	2024-10-21	17	436
3690	13:10:00	14:50:00	2024-10-28	17	436
3691	13:10:00	14:50:00	2024-11-04	17	436
3692	13:10:00	14:50:00	2024-11-11	17	436
3693	13:10:00	14:50:00	2024-11-18	17	436
3694	13:10:00	14:50:00	2024-11-25	17	436
3695	13:10:00	14:50:00	2024-12-02	17	436
3696	13:10:00	14:50:00	2024-12-09	17	436
3697	15:00:00	16:40:00	2024-08-08	17	437
3698	15:00:00	16:40:00	2024-08-15	17	437
3699	15:00:00	16:40:00	2024-08-22	17	437
3700	15:00:00	16:40:00	2024-08-29	17	437
3701	15:00:00	16:40:00	2024-09-05	17	437
3702	15:00:00	16:40:00	2024-09-12	17	437
3703	15:00:00	16:40:00	2024-09-19	17	437
3704	15:00:00	16:40:00	2024-09-26	17	437
3705	15:00:00	16:40:00	2024-10-03	17	437
3706	15:00:00	16:40:00	2024-10-10	17	437
3707	15:00:00	16:40:00	2024-10-17	17	437
3708	15:00:00	16:40:00	2024-10-24	17	437
3709	15:00:00	16:40:00	2024-10-31	17	437
3710	15:00:00	16:40:00	2024-11-07	17	437
3711	15:00:00	16:40:00	2024-11-14	17	437
3712	15:00:00	16:40:00	2024-11-21	17	437
3713	15:00:00	16:40:00	2024-11-28	17	437
3714	15:00:00	16:40:00	2024-12-05	17	437
3715	15:00:00	16:40:00	2024-12-12	17	437
3716	09:20:00	11:00:00	2024-08-05	17	438
3717	09:20:00	11:00:00	2024-08-12	17	438
3718	09:20:00	11:00:00	2024-08-19	17	438
3719	09:20:00	11:00:00	2024-08-26	17	438
3720	09:20:00	11:00:00	2024-09-02	17	438
3721	09:20:00	11:00:00	2024-09-09	17	438
3722	09:20:00	11:00:00	2024-09-16	17	438
3723	09:20:00	11:00:00	2024-09-23	17	438
3724	09:20:00	11:00:00	2024-09-30	17	438
3725	09:20:00	11:00:00	2024-10-07	17	438
3726	09:20:00	11:00:00	2024-10-14	17	438
3727	09:20:00	11:00:00	2024-10-21	17	438
3728	09:20:00	11:00:00	2024-10-28	17	438
3729	09:20:00	11:00:00	2024-11-04	17	438
3730	09:20:00	11:00:00	2024-11-11	17	438
3731	09:20:00	11:00:00	2024-11-18	17	438
3732	09:20:00	11:00:00	2024-11-25	17	438
3733	09:20:00	11:00:00	2024-12-02	17	438
3734	09:20:00	11:00:00	2024-12-09	17	438
3735	07:30:00	09:10:00	2024-08-08	17	439
3736	07:30:00	09:10:00	2024-08-15	17	439
3737	07:30:00	09:10:00	2024-08-22	17	439
3738	07:30:00	09:10:00	2024-08-29	17	439
3739	07:30:00	09:10:00	2024-09-05	17	439
3740	07:30:00	09:10:00	2024-09-12	17	439
3741	07:30:00	09:10:00	2024-09-19	17	439
3742	07:30:00	09:10:00	2024-09-26	17	439
3743	07:30:00	09:10:00	2024-10-03	17	439
3744	07:30:00	09:10:00	2024-10-10	17	439
3745	07:30:00	09:10:00	2024-10-17	17	439
3746	07:30:00	09:10:00	2024-10-24	17	439
3747	07:30:00	09:10:00	2024-10-31	17	439
3748	07:30:00	09:10:00	2024-11-07	17	439
3749	07:30:00	09:10:00	2024-11-14	17	439
3750	07:30:00	09:10:00	2024-11-21	17	439
3751	07:30:00	09:10:00	2024-11-28	17	439
3752	07:30:00	09:10:00	2024-12-05	17	439
3753	07:30:00	09:10:00	2024-12-12	17	439
5173	11:10:00	12:50:00	2024-08-07	32	100
5174	11:10:00	12:50:00	2024-08-14	32	100
5175	11:10:00	12:50:00	2024-08-21	32	100
5176	11:10:00	12:50:00	2024-08-28	32	100
5177	11:10:00	12:50:00	2024-09-04	32	100
5178	11:10:00	12:50:00	2024-09-11	32	100
5179	11:10:00	12:50:00	2024-09-18	32	100
5180	11:10:00	12:50:00	2024-09-25	32	100
5181	11:10:00	12:50:00	2024-10-02	32	100
5182	11:10:00	12:50:00	2024-10-09	32	100
5183	11:10:00	12:50:00	2024-10-16	32	100
5184	11:10:00	12:50:00	2024-10-23	32	100
5185	11:10:00	12:50:00	2024-10-30	32	100
5186	11:10:00	12:50:00	2024-11-06	32	100
5187	11:10:00	12:50:00	2024-11-13	32	100
5188	11:10:00	12:50:00	2024-11-20	32	100
5189	11:10:00	12:50:00	2024-11-27	32	100
5190	11:10:00	12:50:00	2024-12-04	32	100
5191	11:10:00	12:50:00	2024-12-11	32	100
5192	09:20:00	11:00:00	2024-08-09	32	101
5193	09:20:00	11:00:00	2024-08-16	32	101
5194	09:20:00	11:00:00	2024-08-23	32	101
5195	09:20:00	11:00:00	2024-08-30	32	101
5196	09:20:00	11:00:00	2024-09-06	32	101
5197	09:20:00	11:00:00	2024-09-13	32	101
5198	09:20:00	11:00:00	2024-09-20	32	101
5199	09:20:00	11:00:00	2024-09-27	32	101
5200	09:20:00	11:00:00	2024-10-04	32	101
5201	09:20:00	11:00:00	2024-10-11	32	101
5202	09:20:00	11:00:00	2024-10-18	32	101
5203	09:20:00	11:00:00	2024-10-25	32	101
5204	09:20:00	11:00:00	2024-11-01	32	101
5205	09:20:00	11:00:00	2024-11-08	32	101
5206	09:20:00	11:00:00	2024-11-15	32	101
5207	09:20:00	11:00:00	2024-11-22	32	101
5208	09:20:00	11:00:00	2024-11-29	32	101
5209	09:20:00	11:00:00	2024-12-06	32	101
3754	07:30:00	09:10:00	2024-08-05	18	440
3755	07:30:00	09:10:00	2024-08-12	18	440
3756	07:30:00	09:10:00	2024-08-19	18	440
3757	07:30:00	09:10:00	2024-08-26	18	440
3758	07:30:00	09:10:00	2024-09-02	18	440
3759	07:30:00	09:10:00	2024-09-09	18	440
3760	07:30:00	09:10:00	2024-09-16	18	440
3761	07:30:00	09:10:00	2024-09-23	18	440
3762	07:30:00	09:10:00	2024-09-30	18	440
3763	07:30:00	09:10:00	2024-10-07	18	440
3764	07:30:00	09:10:00	2024-10-14	18	440
3765	07:30:00	09:10:00	2024-10-21	18	440
3766	07:30:00	09:10:00	2024-10-28	18	440
3767	07:30:00	09:10:00	2024-11-04	18	440
3768	07:30:00	09:10:00	2024-11-11	18	440
3769	07:30:00	09:10:00	2024-11-18	18	440
3770	07:30:00	09:10:00	2024-11-25	18	440
3771	07:30:00	09:10:00	2024-12-02	18	440
3772	07:30:00	09:10:00	2024-12-09	18	440
3773	09:20:00	11:00:00	2024-08-08	18	441
3774	09:20:00	11:00:00	2024-08-15	18	441
3775	09:20:00	11:00:00	2024-08-22	18	441
3776	09:20:00	11:00:00	2024-08-29	18	441
3777	09:20:00	11:00:00	2024-09-05	18	441
3778	09:20:00	11:00:00	2024-09-12	18	441
3779	09:20:00	11:00:00	2024-09-19	18	441
3780	09:20:00	11:00:00	2024-09-26	18	441
3781	09:20:00	11:00:00	2024-10-03	18	441
3782	09:20:00	11:00:00	2024-10-10	18	441
3783	09:20:00	11:00:00	2024-10-17	18	441
3784	09:20:00	11:00:00	2024-10-24	18	441
3785	09:20:00	11:00:00	2024-10-31	18	441
3786	09:20:00	11:00:00	2024-11-07	18	441
3787	09:20:00	11:00:00	2024-11-14	18	441
3788	09:20:00	11:00:00	2024-11-21	18	441
3789	09:20:00	11:00:00	2024-11-28	18	441
3790	09:20:00	11:00:00	2024-12-05	18	441
3791	09:20:00	11:00:00	2024-12-12	18	441
3792	07:30:00	09:10:00	2024-08-05	20	444
3793	07:30:00	09:10:00	2024-08-12	20	444
3794	07:30:00	09:10:00	2024-08-19	20	444
3795	07:30:00	09:10:00	2024-08-26	20	444
3796	07:30:00	09:10:00	2024-09-02	20	444
3797	07:30:00	09:10:00	2024-09-09	20	444
3798	07:30:00	09:10:00	2024-09-16	20	444
3799	07:30:00	09:10:00	2024-09-23	20	444
3800	07:30:00	09:10:00	2024-09-30	20	444
3801	07:30:00	09:10:00	2024-10-07	20	444
3802	07:30:00	09:10:00	2024-10-14	20	444
3803	07:30:00	09:10:00	2024-10-21	20	444
3804	07:30:00	09:10:00	2024-10-28	20	444
3805	07:30:00	09:10:00	2024-11-04	20	444
3806	07:30:00	09:10:00	2024-11-11	20	444
3807	07:30:00	09:10:00	2024-11-18	20	444
3808	07:30:00	09:10:00	2024-11-25	20	444
3809	07:30:00	09:10:00	2024-12-02	20	444
3810	07:30:00	09:10:00	2024-12-09	20	444
3811	09:20:00	11:00:00	2024-08-07	20	445
3812	09:20:00	11:00:00	2024-08-14	20	445
3813	09:20:00	11:00:00	2024-08-21	20	445
3814	09:20:00	11:00:00	2024-08-28	20	445
3815	09:20:00	11:00:00	2024-09-04	20	445
3816	09:20:00	11:00:00	2024-09-11	20	445
3817	09:20:00	11:00:00	2024-09-18	20	445
3818	09:20:00	11:00:00	2024-09-25	20	445
3819	09:20:00	11:00:00	2024-10-02	20	445
3820	09:20:00	11:00:00	2024-10-09	20	445
3821	09:20:00	11:00:00	2024-10-16	20	445
3822	09:20:00	11:00:00	2024-10-23	20	445
3823	09:20:00	11:00:00	2024-10-30	20	445
3824	09:20:00	11:00:00	2024-11-06	20	445
3825	09:20:00	11:00:00	2024-11-13	20	445
3826	09:20:00	11:00:00	2024-11-20	20	445
3827	09:20:00	11:00:00	2024-11-27	20	445
3828	09:20:00	11:00:00	2024-12-04	20	445
3829	09:20:00	11:00:00	2024-12-11	20	445
3830	09:20:00	11:00:00	2024-08-05	69	442
3831	09:20:00	11:00:00	2024-08-12	69	442
3832	09:20:00	11:00:00	2024-08-19	69	442
3833	09:20:00	11:00:00	2024-08-26	69	442
3834	09:20:00	11:00:00	2024-09-02	69	442
3835	09:20:00	11:00:00	2024-09-09	69	442
3836	09:20:00	11:00:00	2024-09-16	69	442
3837	09:20:00	11:00:00	2024-09-23	69	442
3838	09:20:00	11:00:00	2024-09-30	69	442
3839	09:20:00	11:00:00	2024-10-07	69	442
3840	09:20:00	11:00:00	2024-10-14	69	442
3841	09:20:00	11:00:00	2024-10-21	69	442
3842	09:20:00	11:00:00	2024-10-28	69	442
3843	09:20:00	11:00:00	2024-11-04	69	442
3844	09:20:00	11:00:00	2024-11-11	69	442
3845	09:20:00	11:00:00	2024-11-18	69	442
3846	09:20:00	11:00:00	2024-11-25	69	442
3847	09:20:00	11:00:00	2024-12-02	69	442
3848	09:20:00	11:00:00	2024-12-09	69	442
3849	07:30:00	09:10:00	2024-08-08	69	443
3850	07:30:00	09:10:00	2024-08-15	69	443
3851	07:30:00	09:10:00	2024-08-22	69	443
3852	07:30:00	09:10:00	2024-08-29	69	443
3853	07:30:00	09:10:00	2024-09-05	69	443
3854	07:30:00	09:10:00	2024-09-12	69	443
3855	07:30:00	09:10:00	2024-09-19	69	443
3856	07:30:00	09:10:00	2024-09-26	69	443
3857	07:30:00	09:10:00	2024-10-03	69	443
3858	07:30:00	09:10:00	2024-10-10	69	443
3859	07:30:00	09:10:00	2024-10-17	69	443
3860	07:30:00	09:10:00	2024-10-24	69	443
3861	07:30:00	09:10:00	2024-10-31	69	443
3862	07:30:00	09:10:00	2024-11-07	69	443
3863	07:30:00	09:10:00	2024-11-14	69	443
3864	07:30:00	09:10:00	2024-11-21	69	443
3865	07:30:00	09:10:00	2024-11-28	69	443
3866	07:30:00	09:10:00	2024-12-05	69	443
3867	07:30:00	09:10:00	2024-12-12	69	443
3868	09:20:00	11:00:00	2024-08-05	19	454
3869	09:20:00	11:00:00	2024-08-12	19	454
3870	09:20:00	11:00:00	2024-08-19	19	454
3871	09:20:00	11:00:00	2024-08-26	19	454
3872	09:20:00	11:00:00	2024-09-02	19	454
3873	09:20:00	11:00:00	2024-09-09	19	454
3874	09:20:00	11:00:00	2024-09-16	19	454
3875	09:20:00	11:00:00	2024-09-23	19	454
3876	09:20:00	11:00:00	2024-09-30	19	454
3877	09:20:00	11:00:00	2024-10-07	19	454
3878	09:20:00	11:00:00	2024-10-14	19	454
3879	09:20:00	11:00:00	2024-10-21	19	454
3880	09:20:00	11:00:00	2024-10-28	19	454
3881	09:20:00	11:00:00	2024-11-04	19	454
3882	09:20:00	11:00:00	2024-11-11	19	454
3883	09:20:00	11:00:00	2024-11-18	19	454
3884	09:20:00	11:00:00	2024-11-25	19	454
3885	09:20:00	11:00:00	2024-12-02	19	454
3886	09:20:00	11:00:00	2024-12-09	19	454
3887	07:30:00	09:10:00	2024-08-07	19	455
3888	07:30:00	09:10:00	2024-08-14	19	455
3889	07:30:00	09:10:00	2024-08-21	19	455
3890	07:30:00	09:10:00	2024-08-28	19	455
3891	07:30:00	09:10:00	2024-09-04	19	455
3892	07:30:00	09:10:00	2024-09-11	19	455
3893	07:30:00	09:10:00	2024-09-18	19	455
3894	07:30:00	09:10:00	2024-09-25	19	455
3895	07:30:00	09:10:00	2024-10-02	19	455
3896	07:30:00	09:10:00	2024-10-09	19	455
3897	07:30:00	09:10:00	2024-10-16	19	455
3898	07:30:00	09:10:00	2024-10-23	19	455
3899	07:30:00	09:10:00	2024-10-30	19	455
3900	07:30:00	09:10:00	2024-11-06	19	455
3901	07:30:00	09:10:00	2024-11-13	19	455
3902	07:30:00	09:10:00	2024-11-20	19	455
3903	07:30:00	09:10:00	2024-11-27	19	455
3904	07:30:00	09:10:00	2024-12-04	19	455
3905	07:30:00	09:10:00	2024-12-11	19	455
5321	11:10:00	12:50:00	2024-08-07	22	106
5322	11:10:00	12:50:00	2024-08-14	22	106
5323	11:10:00	12:50:00	2024-08-21	22	106
5324	11:10:00	12:50:00	2024-08-28	22	106
5325	11:10:00	12:50:00	2024-09-04	22	106
5326	11:10:00	12:50:00	2024-09-11	22	106
5327	11:10:00	12:50:00	2024-09-18	22	106
5328	11:10:00	12:50:00	2024-09-25	22	106
5329	11:10:00	12:50:00	2024-10-02	22	106
5330	11:10:00	12:50:00	2024-10-09	22	106
5331	11:10:00	12:50:00	2024-10-16	22	106
5332	11:10:00	12:50:00	2024-10-23	22	106
5333	11:10:00	12:50:00	2024-10-30	22	106
5334	11:10:00	12:50:00	2024-11-06	22	106
5335	11:10:00	12:50:00	2024-11-13	22	106
5336	11:10:00	12:50:00	2024-11-20	22	106
5337	11:10:00	12:50:00	2024-11-27	22	106
5338	11:10:00	12:50:00	2024-12-04	22	106
5339	11:10:00	12:50:00	2024-12-11	22	106
5340	11:10:00	12:50:00	2024-08-09	22	107
5341	11:10:00	12:50:00	2024-08-16	22	107
5342	11:10:00	12:50:00	2024-08-23	22	107
5343	11:10:00	12:50:00	2024-08-30	22	107
5344	11:10:00	12:50:00	2024-09-06	22	107
5345	11:10:00	12:50:00	2024-09-13	22	107
5346	11:10:00	12:50:00	2024-09-20	22	107
5347	11:10:00	12:50:00	2024-09-27	22	107
5348	11:10:00	12:50:00	2024-10-04	22	107
5349	11:10:00	12:50:00	2024-10-11	22	107
5350	11:10:00	12:50:00	2024-10-18	22	107
5351	11:10:00	12:50:00	2024-10-25	22	107
5352	11:10:00	12:50:00	2024-11-01	22	107
5353	11:10:00	12:50:00	2024-11-08	22	107
5354	11:10:00	12:50:00	2024-11-15	22	107
5355	11:10:00	12:50:00	2024-11-22	22	107
5356	11:10:00	12:50:00	2024-11-29	22	107
5357	11:10:00	12:50:00	2024-12-06	22	107
5762	11:10:00	12:50:00	2024-09-27	32	144
5763	11:10:00	12:50:00	2024-10-04	32	144
5764	11:10:00	12:50:00	2024-10-11	32	144
5765	11:10:00	12:50:00	2024-10-18	32	144
5766	11:10:00	12:50:00	2024-10-25	32	144
5767	11:10:00	12:50:00	2024-11-01	32	144
5768	11:10:00	12:50:00	2024-11-08	32	144
5769	11:10:00	12:50:00	2024-11-15	32	144
5770	11:10:00	12:50:00	2024-11-22	32	144
5771	11:10:00	12:50:00	2024-11-29	32	144
5772	11:10:00	12:50:00	2024-12-06	32	144
5906	09:20:00	12:50:00	2024-08-22	39	152
5907	09:20:00	12:50:00	2024-08-29	39	152
5908	09:20:00	12:50:00	2024-09-05	39	152
5909	09:20:00	12:50:00	2024-09-12	39	152
5910	09:20:00	12:50:00	2024-09-19	39	152
5911	09:20:00	12:50:00	2024-09-26	39	152
5912	09:20:00	12:50:00	2024-10-03	39	152
5913	09:20:00	12:50:00	2024-10-10	39	152
5914	09:20:00	12:50:00	2024-10-17	39	152
5915	09:20:00	12:50:00	2024-10-24	39	152
5916	09:20:00	12:50:00	2024-10-31	39	152
5917	09:20:00	12:50:00	2024-11-07	39	152
5918	09:20:00	12:50:00	2024-11-14	39	152
5919	09:20:00	12:50:00	2024-11-21	39	152
5920	09:20:00	12:50:00	2024-11-28	39	152
5921	09:20:00	12:50:00	2024-12-05	39	152
5922	09:20:00	12:50:00	2024-12-12	39	152
5923	14:00:00	17:20:00	2024-08-06	24	154
5924	14:00:00	17:20:00	2024-08-13	24	154
5925	14:00:00	17:20:00	2024-08-20	24	154
5926	14:00:00	17:20:00	2024-08-27	24	154
5927	14:00:00	17:20:00	2024-09-03	24	154
5928	14:00:00	17:20:00	2024-09-10	24	154
5929	14:00:00	17:20:00	2024-09-17	24	154
5930	14:00:00	17:20:00	2024-09-24	24	154
5931	14:00:00	17:20:00	2024-10-01	24	154
5932	14:00:00	17:20:00	2024-10-08	24	154
5933	14:00:00	17:20:00	2024-10-15	24	154
5934	14:00:00	17:20:00	2024-10-22	24	154
5935	14:00:00	17:20:00	2024-10-29	24	154
5936	14:00:00	17:20:00	2024-11-05	24	154
5937	14:00:00	17:20:00	2024-11-12	24	154
5938	14:00:00	17:20:00	2024-11-19	24	154
5939	14:00:00	17:20:00	2024-11-26	24	154
5940	14:00:00	17:20:00	2024-12-03	24	154
5941	14:00:00	17:20:00	2024-12-10	24	154
5942	09:20:00	12:50:00	2024-08-08	24	155
5943	09:20:00	12:50:00	2024-08-15	24	155
5284	07:30:00	09:10:00	2024-08-07	22	104
5285	07:30:00	09:10:00	2024-08-14	22	104
5286	07:30:00	09:10:00	2024-08-21	22	104
5287	07:30:00	09:10:00	2024-08-28	22	104
5288	07:30:00	09:10:00	2024-09-04	22	104
5289	07:30:00	09:10:00	2024-09-11	22	104
5290	07:30:00	09:10:00	2024-09-18	22	104
5291	07:30:00	09:10:00	2024-09-25	22	104
5292	07:30:00	09:10:00	2024-10-02	22	104
5293	07:30:00	09:10:00	2024-10-09	22	104
5294	07:30:00	09:10:00	2024-10-16	22	104
5295	07:30:00	09:10:00	2024-10-23	22	104
5296	07:30:00	09:10:00	2024-10-30	22	104
5297	07:30:00	09:10:00	2024-11-06	22	104
5298	07:30:00	09:10:00	2024-11-13	22	104
5299	07:30:00	09:10:00	2024-11-20	22	104
5300	07:30:00	09:10:00	2024-11-27	22	104
5301	07:30:00	09:10:00	2024-12-04	22	104
5302	07:30:00	09:10:00	2024-12-11	22	104
5303	07:30:00	09:10:00	2024-08-09	22	105
5304	07:30:00	09:10:00	2024-08-16	22	105
5305	07:30:00	09:10:00	2024-08-23	22	105
5306	07:30:00	09:10:00	2024-08-30	22	105
5307	07:30:00	09:10:00	2024-09-06	22	105
5308	07:30:00	09:10:00	2024-09-13	22	105
5309	07:30:00	09:10:00	2024-09-20	22	105
5310	07:30:00	09:10:00	2024-09-27	22	105
5311	07:30:00	09:10:00	2024-10-04	22	105
5312	07:30:00	09:10:00	2024-10-11	22	105
5313	07:30:00	09:10:00	2024-10-18	22	105
5314	07:30:00	09:10:00	2024-10-25	22	105
5315	07:30:00	09:10:00	2024-11-01	22	105
5316	07:30:00	09:10:00	2024-11-08	22	105
5317	07:30:00	09:10:00	2024-11-15	22	105
5318	07:30:00	09:10:00	2024-11-22	22	105
5319	07:30:00	09:10:00	2024-11-29	22	105
5320	07:30:00	09:10:00	2024-12-06	22	105
5358	09:20:00	11:00:00	2024-08-06	22	112
5359	09:20:00	11:00:00	2024-08-13	22	112
5360	09:20:00	11:00:00	2024-08-20	22	112
5361	09:20:00	11:00:00	2024-08-27	22	112
5362	09:20:00	11:00:00	2024-09-03	22	112
5363	09:20:00	11:00:00	2024-09-10	22	112
5364	09:20:00	11:00:00	2024-09-17	22	112
5365	09:20:00	11:00:00	2024-09-24	22	112
5366	09:20:00	11:00:00	2024-10-01	22	112
5367	09:20:00	11:00:00	2024-10-08	22	112
5368	09:20:00	11:00:00	2024-10-15	22	112
5369	09:20:00	11:00:00	2024-10-22	22	112
5370	09:20:00	11:00:00	2024-10-29	22	112
5371	09:20:00	11:00:00	2024-11-05	22	112
5372	09:20:00	11:00:00	2024-11-12	22	112
5373	09:20:00	11:00:00	2024-11-19	22	112
5374	09:20:00	11:00:00	2024-11-26	22	112
5375	09:20:00	11:00:00	2024-12-03	22	112
5376	09:20:00	11:00:00	2024-12-10	22	112
5377	09:20:00	11:00:00	2024-08-08	22	113
5378	09:20:00	11:00:00	2024-08-15	22	113
5379	09:20:00	11:00:00	2024-08-22	22	113
5380	09:20:00	11:00:00	2024-08-29	22	113
5381	09:20:00	11:00:00	2024-09-05	22	113
5382	09:20:00	11:00:00	2024-09-12	22	113
5383	09:20:00	11:00:00	2024-09-19	22	113
5384	09:20:00	11:00:00	2024-09-26	22	113
5385	09:20:00	11:00:00	2024-10-03	22	113
5386	09:20:00	11:00:00	2024-10-10	22	113
5387	09:20:00	11:00:00	2024-10-17	22	113
5388	09:20:00	11:00:00	2024-10-24	22	113
5389	09:20:00	11:00:00	2024-10-31	22	113
5390	09:20:00	11:00:00	2024-11-07	22	113
5391	09:20:00	11:00:00	2024-11-14	22	113
5392	09:20:00	11:00:00	2024-11-21	22	113
5393	09:20:00	11:00:00	2024-11-28	22	113
5394	09:20:00	11:00:00	2024-12-05	22	113
5395	09:20:00	11:00:00	2024-12-12	22	113
5396	07:30:00	11:00:00	2024-08-07	26	123
5397	07:30:00	11:00:00	2024-08-14	26	123
5398	07:30:00	11:00:00	2024-08-21	26	123
5399	07:30:00	11:00:00	2024-08-28	26	123
5400	07:30:00	11:00:00	2024-09-04	26	123
5401	07:30:00	11:00:00	2024-09-11	26	123
5402	07:30:00	11:00:00	2024-09-18	26	123
5403	07:30:00	11:00:00	2024-09-25	26	123
5404	07:30:00	11:00:00	2024-10-02	26	123
5405	07:30:00	11:00:00	2024-10-09	26	123
5406	07:30:00	11:00:00	2024-10-16	26	123
5407	07:30:00	11:00:00	2024-10-23	26	123
5408	07:30:00	11:00:00	2024-10-30	26	123
5409	07:30:00	11:00:00	2024-11-06	26	123
5410	07:30:00	11:00:00	2024-11-13	26	123
5411	07:30:00	11:00:00	2024-11-20	26	123
5412	07:30:00	11:00:00	2024-11-27	26	123
5413	07:30:00	11:00:00	2024-12-04	26	123
5414	07:30:00	11:00:00	2024-12-11	26	123
5415	09:20:00	12:50:00	2024-08-06	21	125
5416	09:20:00	12:50:00	2024-08-13	21	125
5417	09:20:00	12:50:00	2024-08-20	21	125
5418	09:20:00	12:50:00	2024-08-27	21	125
5419	09:20:00	12:50:00	2024-09-03	21	125
5420	09:20:00	12:50:00	2024-09-10	21	125
5421	09:20:00	12:50:00	2024-09-17	21	125
5422	09:20:00	12:50:00	2024-09-24	21	125
5423	09:20:00	12:50:00	2024-10-01	21	125
5424	09:20:00	12:50:00	2024-10-08	21	125
5425	09:20:00	12:50:00	2024-10-15	21	125
5426	09:20:00	12:50:00	2024-10-22	21	125
5427	09:20:00	12:50:00	2024-10-29	21	125
5428	09:20:00	12:50:00	2024-11-05	21	125
5429	09:20:00	12:50:00	2024-11-12	21	125
5430	09:20:00	12:50:00	2024-11-19	21	125
5431	09:20:00	12:50:00	2024-11-26	21	125
5432	09:20:00	12:50:00	2024-12-03	21	125
5433	09:20:00	12:50:00	2024-12-10	21	125
5434	09:20:00	11:00:00	2024-08-05	38	126
5435	09:20:00	11:00:00	2024-08-12	38	126
5436	09:20:00	11:00:00	2024-08-19	38	126
5437	09:20:00	11:00:00	2024-08-26	38	126
5438	09:20:00	11:00:00	2024-09-02	38	126
5439	09:20:00	11:00:00	2024-09-09	38	126
5440	09:20:00	11:00:00	2024-09-16	38	126
5441	09:20:00	11:00:00	2024-09-23	38	126
5442	09:20:00	11:00:00	2024-09-30	38	126
5443	09:20:00	11:00:00	2024-10-07	38	126
5444	09:20:00	11:00:00	2024-10-14	38	126
5445	09:20:00	11:00:00	2024-10-21	38	126
5446	09:20:00	11:00:00	2024-10-28	38	126
5447	09:20:00	11:00:00	2024-11-04	38	126
5448	09:20:00	11:00:00	2024-11-11	38	126
5449	09:20:00	11:00:00	2024-11-18	38	126
5450	09:20:00	11:00:00	2024-11-25	38	126
5451	09:20:00	11:00:00	2024-12-02	38	126
5452	09:20:00	11:00:00	2024-12-09	38	126
5453	07:30:00	09:10:00	2024-08-09	30	127
5454	07:30:00	09:10:00	2024-08-16	30	127
5455	07:30:00	09:10:00	2024-08-23	30	127
5456	07:30:00	09:10:00	2024-08-30	30	127
5457	07:30:00	09:10:00	2024-09-06	30	127
5458	07:30:00	09:10:00	2024-09-13	30	127
5459	07:30:00	09:10:00	2024-09-20	30	127
5460	07:30:00	09:10:00	2024-09-27	30	127
5461	07:30:00	09:10:00	2024-10-04	30	127
5462	07:30:00	09:10:00	2024-10-11	30	127
5463	07:30:00	09:10:00	2024-10-18	30	127
5464	07:30:00	09:10:00	2024-10-25	30	127
5465	07:30:00	09:10:00	2024-11-01	30	127
5466	07:30:00	09:10:00	2024-11-08	30	127
5467	07:30:00	09:10:00	2024-11-15	30	127
5468	07:30:00	09:10:00	2024-11-22	30	127
5469	07:30:00	09:10:00	2024-11-29	30	127
5470	07:30:00	09:10:00	2024-12-06	30	127
5471	09:20:00	11:00:00	2024-08-09	30	128
5472	09:20:00	11:00:00	2024-08-16	30	128
5473	09:20:00	11:00:00	2024-08-23	30	128
5474	09:20:00	11:00:00	2024-08-30	30	128
5475	09:20:00	11:00:00	2024-09-06	30	128
5476	09:20:00	11:00:00	2024-09-13	30	128
5477	09:20:00	11:00:00	2024-09-20	30	128
5478	09:20:00	11:00:00	2024-09-27	30	128
5479	09:20:00	11:00:00	2024-10-04	30	128
5480	09:20:00	11:00:00	2024-10-11	30	128
5481	09:20:00	11:00:00	2024-10-18	30	128
5482	09:20:00	11:00:00	2024-10-25	30	128
5483	09:20:00	11:00:00	2024-11-01	30	128
5484	09:20:00	11:00:00	2024-11-08	30	128
5485	09:20:00	11:00:00	2024-11-15	30	128
5486	09:20:00	11:00:00	2024-11-22	30	128
5487	09:20:00	11:00:00	2024-11-29	30	128
5488	09:20:00	11:00:00	2024-12-06	30	128
5527	15:00:00	16:40:00	2024-08-05	30	131
5528	15:00:00	16:40:00	2024-08-12	30	131
5529	15:00:00	16:40:00	2024-08-19	30	131
5530	15:00:00	16:40:00	2024-08-26	30	131
5531	15:00:00	16:40:00	2024-09-02	30	131
5532	15:00:00	16:40:00	2024-09-09	30	131
5533	15:00:00	16:40:00	2024-09-16	30	131
5534	15:00:00	16:40:00	2024-09-23	30	131
5535	15:00:00	16:40:00	2024-09-30	30	131
5536	15:00:00	16:40:00	2024-10-07	30	131
5537	15:00:00	16:40:00	2024-10-14	30	131
5538	15:00:00	16:40:00	2024-10-21	30	131
5539	15:00:00	16:40:00	2024-10-28	30	131
5540	15:00:00	16:40:00	2024-11-04	30	131
5541	15:00:00	16:40:00	2024-11-11	30	131
5542	15:00:00	16:40:00	2024-11-18	30	131
5543	15:00:00	16:40:00	2024-11-25	30	131
5544	15:00:00	16:40:00	2024-12-02	30	131
5545	15:00:00	16:40:00	2024-12-09	30	131
5546	13:10:00	14:50:00	2024-08-07	30	132
5547	13:10:00	14:50:00	2024-08-14	30	132
5548	13:10:00	14:50:00	2024-08-21	30	132
5549	13:10:00	14:50:00	2024-08-28	30	132
5550	13:10:00	14:50:00	2024-09-04	30	132
5551	13:10:00	14:50:00	2024-09-11	30	132
5552	13:10:00	14:50:00	2024-09-18	30	132
5553	13:10:00	14:50:00	2024-09-25	30	132
5554	13:10:00	14:50:00	2024-10-02	30	132
5555	13:10:00	14:50:00	2024-10-09	30	132
5556	13:10:00	14:50:00	2024-10-16	30	132
5557	13:10:00	14:50:00	2024-10-23	30	132
5558	13:10:00	14:50:00	2024-10-30	30	132
5559	13:10:00	14:50:00	2024-11-06	30	132
5560	13:10:00	14:50:00	2024-11-13	30	132
5561	13:10:00	14:50:00	2024-11-20	30	132
5562	13:10:00	14:50:00	2024-11-27	30	132
5563	13:10:00	14:50:00	2024-12-04	30	132
5564	13:10:00	14:50:00	2024-12-11	30	132
5603	15:00:00	16:40:00	2024-08-05	31	135
5604	15:00:00	16:40:00	2024-08-12	31	135
5605	15:00:00	16:40:00	2024-08-19	31	135
5606	15:00:00	16:40:00	2024-08-26	31	135
5607	15:00:00	16:40:00	2024-09-02	31	135
5608	15:00:00	16:40:00	2024-09-09	31	135
5609	15:00:00	16:40:00	2024-09-16	31	135
5610	15:00:00	16:40:00	2024-09-23	31	135
5611	15:00:00	16:40:00	2024-09-30	31	135
5612	15:00:00	16:40:00	2024-10-07	31	135
5613	15:00:00	16:40:00	2024-10-14	31	135
5614	15:00:00	16:40:00	2024-10-21	31	135
5615	15:00:00	16:40:00	2024-10-28	31	135
5616	15:00:00	16:40:00	2024-11-04	31	135
5617	15:00:00	16:40:00	2024-11-11	31	135
5618	15:00:00	16:40:00	2024-11-18	31	135
5619	15:00:00	16:40:00	2024-11-25	31	135
5620	15:00:00	16:40:00	2024-12-02	31	135
5621	15:00:00	16:40:00	2024-12-09	31	135
5622	13:10:00	14:50:00	2024-08-07	31	136
5623	13:10:00	14:50:00	2024-08-14	31	136
5624	13:10:00	14:50:00	2024-08-21	31	136
5625	13:10:00	14:50:00	2024-08-28	31	136
5626	13:10:00	14:50:00	2024-09-04	31	136
5627	13:10:00	14:50:00	2024-09-11	31	136
5628	13:10:00	14:50:00	2024-09-18	31	136
5629	13:10:00	14:50:00	2024-09-25	31	136
5630	13:10:00	14:50:00	2024-10-02	31	136
5631	13:10:00	14:50:00	2024-10-09	31	136
5632	13:10:00	14:50:00	2024-10-16	31	136
5633	13:10:00	14:50:00	2024-10-23	31	136
4187	17:00:00	18:40:00	2024-08-09	4	468
4188	17:00:00	18:40:00	2024-08-16	4	468
4189	17:00:00	18:40:00	2024-08-23	4	468
4190	17:00:00	18:40:00	2024-08-30	4	468
4191	17:00:00	18:40:00	2024-09-13	4	468
4192	17:00:00	18:40:00	2024-09-20	4	468
4193	17:00:00	18:40:00	2024-09-27	4	468
4194	17:00:00	18:40:00	2024-10-04	4	468
4195	17:00:00	18:40:00	2024-10-11	4	468
4196	17:00:00	18:40:00	2024-10-18	4	468
4197	17:00:00	18:40:00	2024-10-25	4	468
4198	17:00:00	18:40:00	2024-11-01	4	468
4199	17:00:00	18:40:00	2024-11-08	4	468
4200	17:00:00	18:40:00	2024-11-22	4	468
4201	17:00:00	18:40:00	2024-11-29	4	468
4202	17:00:00	18:40:00	2024-12-06	4	468
4203	09:20:00	11:00:00	2024-08-05	2	469
4204	09:20:00	11:00:00	2024-08-12	2	469
4205	09:20:00	11:00:00	2024-08-19	2	469
4206	09:20:00	11:00:00	2024-08-26	2	469
4207	09:20:00	11:00:00	2024-09-02	2	469
4208	09:20:00	11:00:00	2024-09-09	2	469
4209	09:20:00	11:00:00	2024-09-16	2	469
4210	09:20:00	11:00:00	2024-09-23	2	469
4211	09:20:00	11:00:00	2024-09-30	2	469
4212	09:20:00	11:00:00	2024-10-07	2	469
4213	09:20:00	11:00:00	2024-10-14	2	469
4214	09:20:00	11:00:00	2024-10-21	2	469
4215	09:20:00	11:00:00	2024-10-28	2	469
4216	09:20:00	11:00:00	2024-11-04	2	469
4217	09:20:00	11:00:00	2024-11-11	2	469
4218	09:20:00	11:00:00	2024-11-18	2	469
4219	09:20:00	11:00:00	2024-11-25	2	469
4220	09:20:00	11:00:00	2024-12-02	2	469
4221	09:20:00	11:00:00	2024-12-09	2	469
4222	13:10:00	14:50:00	2024-08-07	2	470
4223	13:10:00	14:50:00	2024-08-14	2	470
4224	13:10:00	14:50:00	2024-08-21	2	470
4225	13:10:00	14:50:00	2024-08-28	2	470
4226	13:10:00	14:50:00	2024-09-04	2	470
4227	13:10:00	14:50:00	2024-09-11	2	470
4228	13:10:00	14:50:00	2024-09-18	2	470
4229	13:10:00	14:50:00	2024-09-25	2	470
4230	13:10:00	14:50:00	2024-10-02	2	470
4231	13:10:00	14:50:00	2024-10-09	2	470
4232	13:10:00	14:50:00	2024-10-16	2	470
4233	13:10:00	14:50:00	2024-10-23	2	470
4234	13:10:00	14:50:00	2024-10-30	2	470
4235	13:10:00	14:50:00	2024-11-06	2	470
4236	13:10:00	14:50:00	2024-11-13	2	470
4237	13:10:00	14:50:00	2024-11-20	2	470
4238	13:10:00	14:50:00	2024-11-27	2	470
4239	13:10:00	14:50:00	2024-12-04	2	470
4240	13:10:00	14:50:00	2024-12-11	2	470
4241	09:20:00	11:00:00	2024-08-06	7	395
4242	09:20:00	11:00:00	2024-08-13	7	395
4243	09:20:00	11:00:00	2024-08-20	7	395
4244	09:20:00	11:00:00	2024-08-27	7	395
4245	09:20:00	11:00:00	2024-09-03	7	395
4246	09:20:00	11:00:00	2024-09-10	7	395
4247	09:20:00	11:00:00	2024-09-17	7	395
4248	09:20:00	11:00:00	2024-09-24	7	395
4249	09:20:00	11:00:00	2024-10-01	7	395
4250	09:20:00	11:00:00	2024-10-08	7	395
4251	09:20:00	11:00:00	2024-10-15	7	395
4252	09:20:00	11:00:00	2024-10-22	7	395
4253	09:20:00	11:00:00	2024-10-29	7	395
4254	09:20:00	11:00:00	2024-11-05	7	395
4255	09:20:00	11:00:00	2024-11-12	7	395
4256	09:20:00	11:00:00	2024-11-19	7	395
4257	09:20:00	11:00:00	2024-11-26	7	395
4258	09:20:00	11:00:00	2024-12-03	7	395
4259	09:20:00	11:00:00	2024-12-10	7	395
4260	09:20:00	11:00:00	2024-08-07	7	396
4261	09:20:00	11:00:00	2024-08-14	7	396
4262	09:20:00	11:00:00	2024-08-21	7	396
4263	09:20:00	11:00:00	2024-08-28	7	396
4264	09:20:00	11:00:00	2024-09-04	7	396
4265	09:20:00	11:00:00	2024-09-11	7	396
4266	09:20:00	11:00:00	2024-09-18	7	396
4267	09:20:00	11:00:00	2024-09-25	7	396
4268	09:20:00	11:00:00	2024-10-02	7	396
4269	09:20:00	11:00:00	2024-10-09	7	396
4270	09:20:00	11:00:00	2024-10-16	7	396
4271	09:20:00	11:00:00	2024-10-23	7	396
4272	09:20:00	11:00:00	2024-10-30	7	396
4273	09:20:00	11:00:00	2024-11-06	7	396
4274	09:20:00	11:00:00	2024-11-13	7	396
4275	09:20:00	11:00:00	2024-11-20	7	396
4276	09:20:00	11:00:00	2024-11-27	7	396
4277	09:20:00	11:00:00	2024-12-04	7	396
4278	09:20:00	11:00:00	2024-12-11	7	396
4279	09:20:00	11:00:00	2024-08-06	5	397
4280	09:20:00	11:00:00	2024-08-13	5	397
4281	09:20:00	11:00:00	2024-08-20	5	397
4282	09:20:00	11:00:00	2024-08-27	5	397
4283	09:20:00	11:00:00	2024-09-03	5	397
4284	09:20:00	11:00:00	2024-09-10	5	397
4285	09:20:00	11:00:00	2024-09-17	5	397
4286	09:20:00	11:00:00	2024-09-24	5	397
4287	09:20:00	11:00:00	2024-10-01	5	397
4288	09:20:00	11:00:00	2024-10-08	5	397
4289	09:20:00	11:00:00	2024-10-15	5	397
4290	09:20:00	11:00:00	2024-10-22	5	397
4291	09:20:00	11:00:00	2024-10-29	5	397
4292	09:20:00	11:00:00	2024-11-05	5	397
4293	09:20:00	11:00:00	2024-11-12	5	397
4294	09:20:00	11:00:00	2024-11-19	5	397
4295	09:20:00	11:00:00	2024-11-26	5	397
4296	09:20:00	11:00:00	2024-12-03	5	397
4297	09:20:00	11:00:00	2024-12-10	5	397
4298	09:20:00	11:00:00	2024-08-07	5	398
4299	09:20:00	11:00:00	2024-08-14	5	398
4300	09:20:00	11:00:00	2024-08-21	5	398
4301	09:20:00	11:00:00	2024-08-28	5	398
4302	09:20:00	11:00:00	2024-09-04	5	398
4303	09:20:00	11:00:00	2024-09-11	5	398
4304	09:20:00	11:00:00	2024-09-18	5	398
4305	09:20:00	11:00:00	2024-09-25	5	398
4306	09:20:00	11:00:00	2024-10-02	5	398
4307	09:20:00	11:00:00	2024-10-09	5	398
4308	09:20:00	11:00:00	2024-10-16	5	398
4309	09:20:00	11:00:00	2024-10-23	5	398
4310	09:20:00	11:00:00	2024-10-30	5	398
4311	09:20:00	11:00:00	2024-11-06	5	398
4312	09:20:00	11:00:00	2024-11-13	5	398
4313	09:20:00	11:00:00	2024-11-20	5	398
4314	09:20:00	11:00:00	2024-11-27	5	398
4315	09:20:00	11:00:00	2024-12-04	5	398
4316	09:20:00	11:00:00	2024-12-11	5	398
5489	07:30:00	09:10:00	2024-08-05	24	129
5490	07:30:00	09:10:00	2024-08-12	24	129
5491	07:30:00	09:10:00	2024-08-19	24	129
5492	07:30:00	09:10:00	2024-08-26	24	129
5493	07:30:00	09:10:00	2024-09-02	24	129
5494	07:30:00	09:10:00	2024-09-09	24	129
5495	07:30:00	09:10:00	2024-09-16	24	129
5496	07:30:00	09:10:00	2024-09-23	24	129
5497	07:30:00	09:10:00	2024-09-30	24	129
5498	07:30:00	09:10:00	2024-10-07	24	129
5499	07:30:00	09:10:00	2024-10-14	24	129
5500	07:30:00	09:10:00	2024-10-21	24	129
5501	07:30:00	09:10:00	2024-10-28	24	129
5502	07:30:00	09:10:00	2024-11-04	24	129
5503	07:30:00	09:10:00	2024-11-11	24	129
5504	07:30:00	09:10:00	2024-11-18	24	129
5505	07:30:00	09:10:00	2024-11-25	24	129
5506	07:30:00	09:10:00	2024-12-02	24	129
5507	07:30:00	09:10:00	2024-12-09	24	129
4336	13:10:00	14:50:00	2024-08-05	4	472
4337	13:10:00	14:50:00	2024-08-12	4	472
4338	13:10:00	14:50:00	2024-08-19	4	472
4339	13:10:00	14:50:00	2024-08-26	4	472
4340	13:10:00	14:50:00	2024-09-02	4	472
4341	13:10:00	14:50:00	2024-09-09	4	472
4342	13:10:00	14:50:00	2024-09-16	4	472
4343	13:10:00	14:50:00	2024-09-23	4	472
4344	13:10:00	14:50:00	2024-09-30	4	472
4345	13:10:00	14:50:00	2024-10-07	4	472
4346	13:10:00	14:50:00	2024-10-14	4	472
4347	13:10:00	14:50:00	2024-10-21	4	472
4348	13:10:00	14:50:00	2024-10-28	4	472
4349	13:10:00	14:50:00	2024-11-04	4	472
4350	13:10:00	14:50:00	2024-11-11	4	472
4351	13:10:00	14:50:00	2024-11-18	4	472
4352	13:10:00	14:50:00	2024-11-25	4	472
4353	13:10:00	14:50:00	2024-12-02	4	472
4354	13:10:00	14:50:00	2024-12-09	4	472
4355	09:20:00	11:00:00	2024-08-05	4	471
4356	09:20:00	11:00:00	2024-08-12	4	471
4357	09:20:00	11:00:00	2024-08-19	4	471
4358	09:20:00	11:00:00	2024-08-26	4	471
4359	09:20:00	11:00:00	2024-09-02	4	471
4360	09:20:00	11:00:00	2024-09-09	4	471
4361	09:20:00	11:00:00	2024-09-16	4	471
4362	09:20:00	11:00:00	2024-09-23	4	471
4363	09:20:00	11:00:00	2024-09-30	4	471
4364	09:20:00	11:00:00	2024-10-07	4	471
4365	09:20:00	11:00:00	2024-10-14	4	471
4366	09:20:00	11:00:00	2024-10-21	4	471
4367	09:20:00	11:00:00	2024-10-28	4	471
4368	09:20:00	11:00:00	2024-11-04	4	471
4369	09:20:00	11:00:00	2024-11-11	4	471
4370	09:20:00	11:00:00	2024-11-18	4	471
4371	09:20:00	11:00:00	2024-11-25	4	471
4372	09:20:00	11:00:00	2024-12-02	4	471
4373	09:20:00	11:00:00	2024-12-09	4	471
5508	07:30:00	09:10:00	2024-08-07	24	130
5509	07:30:00	09:10:00	2024-08-14	24	130
5510	07:30:00	09:10:00	2024-08-21	24	130
5511	07:30:00	09:10:00	2024-08-28	24	130
5512	07:30:00	09:10:00	2024-09-04	24	130
5513	07:30:00	09:10:00	2024-09-11	24	130
5514	07:30:00	09:10:00	2024-09-18	24	130
5515	07:30:00	09:10:00	2024-09-25	24	130
5516	07:30:00	09:10:00	2024-10-02	24	130
5517	07:30:00	09:10:00	2024-10-09	24	130
5518	07:30:00	09:10:00	2024-10-16	24	130
5519	07:30:00	09:10:00	2024-10-23	24	130
5520	07:30:00	09:10:00	2024-10-30	24	130
5521	07:30:00	09:10:00	2024-11-06	24	130
5522	07:30:00	09:10:00	2024-11-13	24	130
5523	07:30:00	09:10:00	2024-11-20	24	130
5524	07:30:00	09:10:00	2024-11-27	24	130
5525	07:30:00	09:10:00	2024-12-04	24	130
5526	07:30:00	09:10:00	2024-12-11	24	130
5565	15:00:00	16:40:00	2024-08-05	33	133
5566	15:00:00	16:40:00	2024-08-12	33	133
5567	15:00:00	16:40:00	2024-08-19	33	133
5568	15:00:00	16:40:00	2024-08-26	33	133
5569	15:00:00	16:40:00	2024-09-02	33	133
5570	15:00:00	16:40:00	2024-09-09	33	133
5571	15:00:00	16:40:00	2024-09-16	33	133
5572	15:00:00	16:40:00	2024-09-23	33	133
5573	15:00:00	16:40:00	2024-09-30	33	133
5574	15:00:00	16:40:00	2024-10-07	33	133
5575	15:00:00	16:40:00	2024-10-14	33	133
5576	15:00:00	16:40:00	2024-10-21	33	133
5577	15:00:00	16:40:00	2024-10-28	33	133
5578	15:00:00	16:40:00	2024-11-04	33	133
5579	15:00:00	16:40:00	2024-11-11	33	133
5580	15:00:00	16:40:00	2024-11-18	33	133
5581	15:00:00	16:40:00	2024-11-25	33	133
5582	15:00:00	16:40:00	2024-12-02	33	133
5583	15:00:00	16:40:00	2024-12-09	33	133
5584	13:10:00	14:50:00	2024-08-07	33	134
5585	13:10:00	14:50:00	2024-08-14	33	134
5586	13:10:00	14:50:00	2024-08-21	33	134
5587	13:10:00	14:50:00	2024-08-28	33	134
5588	13:10:00	14:50:00	2024-09-04	33	134
5589	13:10:00	14:50:00	2024-09-11	33	134
5590	13:10:00	14:50:00	2024-09-18	33	134
5591	13:10:00	14:50:00	2024-09-25	33	134
5592	13:10:00	14:50:00	2024-10-02	33	134
5593	13:10:00	14:50:00	2024-10-09	33	134
5594	13:10:00	14:50:00	2024-10-16	33	134
5595	13:10:00	14:50:00	2024-10-23	33	134
5596	13:10:00	14:50:00	2024-10-30	33	134
6007	07:30:00	09:10:00	2024-10-01	65	157
6008	07:30:00	09:10:00	2024-10-08	65	157
6009	07:30:00	09:10:00	2024-10-15	65	157
6010	07:30:00	09:10:00	2024-10-22	65	157
6011	07:30:00	09:10:00	2024-10-29	65	157
6012	07:30:00	09:10:00	2024-11-05	65	157
6013	07:30:00	09:10:00	2024-11-12	65	157
6014	07:30:00	09:10:00	2024-11-19	65	157
6015	07:30:00	09:10:00	2024-11-26	65	157
6016	07:30:00	09:10:00	2024-12-03	65	157
6017	07:30:00	09:10:00	2024-12-10	65	157
6056	15:50:00	17:30:00	2024-08-05	39	160
6057	15:50:00	17:30:00	2024-08-12	39	160
6058	15:50:00	17:30:00	2024-08-19	39	160
6059	15:50:00	17:30:00	2024-08-26	39	160
6060	15:50:00	17:30:00	2024-09-02	39	160
6061	15:50:00	17:30:00	2024-09-09	39	160
6062	15:50:00	17:30:00	2024-09-16	39	160
6063	15:50:00	17:30:00	2024-09-23	39	160
6064	15:50:00	17:30:00	2024-09-30	39	160
6065	15:50:00	17:30:00	2024-10-07	39	160
6066	15:50:00	17:30:00	2024-10-14	39	160
6067	15:50:00	17:30:00	2024-10-21	39	160
6068	15:50:00	17:30:00	2024-10-28	39	160
6069	15:50:00	17:30:00	2024-11-04	39	160
6070	15:50:00	17:30:00	2024-11-11	39	160
6071	15:50:00	17:30:00	2024-11-18	39	160
6072	15:50:00	17:30:00	2024-11-25	39	160
6073	15:50:00	17:30:00	2024-12-02	39	160
6074	15:50:00	17:30:00	2024-12-09	39	160
6075	14:00:00	15:40:00	2024-08-08	39	161
6076	14:00:00	15:40:00	2024-08-15	39	161
6077	14:00:00	15:40:00	2024-08-22	39	161
6078	14:00:00	15:40:00	2024-08-29	39	161
6079	14:00:00	15:40:00	2024-09-05	39	161
6080	14:00:00	15:40:00	2024-09-12	39	161
6081	14:00:00	15:40:00	2024-09-19	39	161
6082	14:00:00	15:40:00	2024-09-26	39	161
6083	14:00:00	15:40:00	2024-10-03	39	161
6084	14:00:00	15:40:00	2024-10-10	39	161
6085	14:00:00	15:40:00	2024-10-17	39	161
6086	14:00:00	15:40:00	2024-10-24	39	161
6087	14:00:00	15:40:00	2024-10-31	39	161
6088	14:00:00	15:40:00	2024-11-07	39	161
6089	14:00:00	15:40:00	2024-11-14	39	161
6090	14:00:00	15:40:00	2024-11-21	39	161
6091	14:00:00	15:40:00	2024-11-28	39	161
6092	14:00:00	15:40:00	2024-12-05	39	161
6093	14:00:00	15:40:00	2024-12-12	39	161
6132	16:50:00	20:10:00	2024-08-05	32	164
6133	16:50:00	20:10:00	2024-08-12	32	164
6134	16:50:00	20:10:00	2024-08-19	32	164
6135	16:50:00	20:10:00	2024-08-26	32	164
6136	16:50:00	20:10:00	2024-09-02	32	164
6137	16:50:00	20:10:00	2024-09-09	32	164
6138	16:50:00	20:10:00	2024-09-16	32	164
6139	16:50:00	20:10:00	2024-09-23	32	164
6140	16:50:00	20:10:00	2024-09-30	32	164
6141	16:50:00	20:10:00	2024-10-07	32	164
6142	16:50:00	20:10:00	2024-10-14	32	164
6143	16:50:00	20:10:00	2024-10-21	32	164
6144	16:50:00	20:10:00	2024-10-28	32	164
6145	16:50:00	20:10:00	2024-11-04	32	164
6146	16:50:00	20:10:00	2024-11-11	32	164
6147	16:50:00	20:10:00	2024-11-18	32	164
6148	16:50:00	20:10:00	2024-11-25	32	164
6149	16:50:00	20:10:00	2024-12-02	32	164
6150	16:50:00	20:10:00	2024-12-09	32	164
6018	11:10:00	12:50:00	2024-08-05	74	158
6019	11:10:00	12:50:00	2024-08-12	74	158
6020	11:10:00	12:50:00	2024-08-19	74	158
6021	11:10:00	12:50:00	2024-08-26	74	158
6022	11:10:00	12:50:00	2024-09-02	74	158
6023	11:10:00	12:50:00	2024-09-09	74	158
6024	11:10:00	12:50:00	2024-09-16	74	158
6025	11:10:00	12:50:00	2024-09-23	74	158
6026	11:10:00	12:50:00	2024-09-30	74	158
6027	11:10:00	12:50:00	2024-10-07	74	158
6028	11:10:00	12:50:00	2024-10-14	74	158
6029	11:10:00	12:50:00	2024-10-21	74	158
6030	11:10:00	12:50:00	2024-10-28	74	158
6031	11:10:00	12:50:00	2024-11-04	74	158
6032	11:10:00	12:50:00	2024-11-11	74	158
6033	11:10:00	12:50:00	2024-11-18	74	158
6034	11:10:00	12:50:00	2024-11-25	74	158
6035	11:10:00	12:50:00	2024-12-02	74	158
6036	11:10:00	12:50:00	2024-12-09	74	158
6037	07:30:00	09:10:00	2024-08-07	74	159
6038	07:30:00	09:10:00	2024-08-14	74	159
6039	07:30:00	09:10:00	2024-08-21	74	159
6040	07:30:00	09:10:00	2024-08-28	74	159
6041	07:30:00	09:10:00	2024-09-04	74	159
6042	07:30:00	09:10:00	2024-09-11	74	159
6043	07:30:00	09:10:00	2024-09-18	74	159
6044	07:30:00	09:10:00	2024-09-25	74	159
6045	07:30:00	09:10:00	2024-10-02	74	159
6046	07:30:00	09:10:00	2024-10-09	74	159
6047	07:30:00	09:10:00	2024-10-16	74	159
6048	07:30:00	09:10:00	2024-10-23	74	159
6049	07:30:00	09:10:00	2024-10-30	74	159
6050	07:30:00	09:10:00	2024-11-06	74	159
6051	07:30:00	09:10:00	2024-11-13	74	159
6052	07:30:00	09:10:00	2024-11-20	74	159
6053	07:30:00	09:10:00	2024-11-27	74	159
6054	07:30:00	09:10:00	2024-12-04	74	159
6055	07:30:00	09:10:00	2024-12-11	74	159
6094	16:50:00	18:30:00	2024-08-05	74	162
6095	16:50:00	18:30:00	2024-08-12	74	162
6096	16:50:00	18:30:00	2024-08-19	74	162
6097	16:50:00	18:30:00	2024-08-26	74	162
6098	16:50:00	18:30:00	2024-09-02	74	162
6099	16:50:00	18:30:00	2024-09-09	74	162
6100	16:50:00	18:30:00	2024-09-16	74	162
6101	16:50:00	18:30:00	2024-09-23	74	162
6102	16:50:00	18:30:00	2024-09-30	74	162
6103	16:50:00	18:30:00	2024-10-07	74	162
6104	16:50:00	18:30:00	2024-10-14	74	162
6105	16:50:00	18:30:00	2024-10-21	74	162
6106	16:50:00	18:30:00	2024-10-28	74	162
6107	16:50:00	18:30:00	2024-11-04	74	162
6108	16:50:00	18:30:00	2024-11-11	74	162
6109	16:50:00	18:30:00	2024-11-18	74	162
6110	16:50:00	18:30:00	2024-11-25	74	162
6111	16:50:00	18:30:00	2024-12-02	74	162
6112	16:50:00	18:30:00	2024-12-09	74	162
6113	15:00:00	16:40:00	2024-08-07	74	163
6114	15:00:00	16:40:00	2024-08-14	74	163
6115	15:00:00	16:40:00	2024-08-21	74	163
6116	15:00:00	16:40:00	2024-08-28	74	163
6117	15:00:00	16:40:00	2024-09-04	74	163
6118	15:00:00	16:40:00	2024-09-11	74	163
6119	15:00:00	16:40:00	2024-09-18	74	163
6120	15:00:00	16:40:00	2024-09-25	74	163
6121	15:00:00	16:40:00	2024-10-02	74	163
6122	15:00:00	16:40:00	2024-10-09	74	163
6123	15:00:00	16:40:00	2024-10-16	74	163
6124	15:00:00	16:40:00	2024-10-23	74	163
6125	15:00:00	16:40:00	2024-10-30	74	163
6126	15:00:00	16:40:00	2024-11-06	74	163
6127	15:00:00	16:40:00	2024-11-13	74	163
6128	15:00:00	16:40:00	2024-11-20	74	163
6129	15:00:00	16:40:00	2024-11-27	74	163
6130	15:00:00	16:40:00	2024-12-04	74	163
6131	15:00:00	16:40:00	2024-12-11	74	163
6151	16:50:00	18:30:00	2024-08-06	39	165
6152	16:50:00	18:30:00	2024-08-13	39	165
6153	16:50:00	18:30:00	2024-08-20	39	165
6154	16:50:00	18:30:00	2024-08-27	39	165
6155	16:50:00	18:30:00	2024-09-03	39	165
6156	16:50:00	18:30:00	2024-09-10	39	165
6157	16:50:00	18:30:00	2024-09-17	39	165
6158	16:50:00	18:30:00	2024-09-24	39	165
6159	16:50:00	18:30:00	2024-10-01	39	165
6160	16:50:00	18:30:00	2024-10-08	39	165
6161	16:50:00	18:30:00	2024-10-15	39	165
6162	16:50:00	18:30:00	2024-10-22	39	165
6163	16:50:00	18:30:00	2024-10-29	39	165
6164	16:50:00	18:30:00	2024-11-05	39	165
6165	16:50:00	18:30:00	2024-11-12	39	165
6166	16:50:00	18:30:00	2024-11-19	39	165
6167	16:50:00	18:30:00	2024-11-26	39	165
6168	16:50:00	18:30:00	2024-12-03	39	165
6169	16:50:00	18:30:00	2024-12-10	39	165
6170	16:50:00	18:30:00	2024-08-08	39	166
6171	16:50:00	18:30:00	2024-08-15	39	166
6172	16:50:00	18:30:00	2024-08-22	39	166
6173	16:50:00	18:30:00	2024-08-29	39	166
6174	16:50:00	18:30:00	2024-09-05	39	166
6175	16:50:00	18:30:00	2024-09-12	39	166
6176	16:50:00	18:30:00	2024-09-19	39	166
6177	16:50:00	18:30:00	2024-09-26	39	166
6178	16:50:00	18:30:00	2024-10-03	39	166
6179	16:50:00	18:30:00	2024-10-10	39	166
6180	16:50:00	18:30:00	2024-10-17	39	166
6181	16:50:00	18:30:00	2024-10-24	39	166
6182	16:50:00	18:30:00	2024-10-31	39	166
6183	16:50:00	18:30:00	2024-11-07	39	166
6184	16:50:00	18:30:00	2024-11-14	39	166
6185	16:50:00	18:30:00	2024-11-21	39	166
6186	16:50:00	18:30:00	2024-11-28	39	166
6187	16:50:00	18:30:00	2024-12-05	39	166
6188	16:50:00	18:30:00	2024-12-12	39	166
6189	13:10:00	16:40:00	2024-08-07	26	167
6190	13:10:00	16:40:00	2024-08-14	26	167
6191	13:10:00	16:40:00	2024-08-21	26	167
6192	13:10:00	16:40:00	2024-08-28	26	167
6193	13:10:00	16:40:00	2024-09-04	26	167
6194	13:10:00	16:40:00	2024-09-11	26	167
6195	13:10:00	16:40:00	2024-09-18	26	167
6196	13:10:00	16:40:00	2024-09-25	26	167
6197	13:10:00	16:40:00	2024-10-02	26	167
6198	13:10:00	16:40:00	2024-10-09	26	167
6199	13:10:00	16:40:00	2024-10-16	26	167
6200	13:10:00	16:40:00	2024-10-23	26	167
6201	13:10:00	16:40:00	2024-10-30	26	167
6202	13:10:00	16:40:00	2024-11-06	26	167
6203	13:10:00	16:40:00	2024-11-13	26	167
6204	13:10:00	16:40:00	2024-11-20	26	167
6205	13:10:00	16:40:00	2024-11-27	26	167
6206	13:10:00	16:40:00	2024-12-04	26	167
6207	13:10:00	16:40:00	2024-12-11	26	167
6208	18:40:00	20:20:00	2024-08-05	68	473
6209	18:40:00	20:20:00	2024-08-12	68	473
6210	18:40:00	20:20:00	2024-08-19	68	473
6211	18:40:00	20:20:00	2024-08-26	68	473
6212	18:40:00	20:20:00	2024-09-02	68	473
6213	18:40:00	20:20:00	2024-09-09	68	473
6214	18:40:00	20:20:00	2024-09-16	68	473
6215	18:40:00	20:20:00	2024-09-23	68	473
6216	18:40:00	20:20:00	2024-09-30	68	473
6217	18:40:00	20:20:00	2024-10-07	68	473
6218	18:40:00	20:20:00	2024-10-14	68	473
6219	18:40:00	20:20:00	2024-10-21	68	473
6220	18:40:00	20:20:00	2024-10-28	68	473
6221	18:40:00	20:20:00	2024-11-04	68	473
6222	18:40:00	20:20:00	2024-11-11	68	473
6223	18:40:00	20:20:00	2024-11-18	68	473
6224	18:40:00	20:20:00	2024-11-25	68	473
6225	18:40:00	20:20:00	2024-12-02	68	473
6226	18:40:00	20:20:00	2024-12-09	68	473
6227	18:40:00	20:20:00	2024-08-06	68	168
6228	18:40:00	20:20:00	2024-08-13	68	168
6229	18:40:00	20:20:00	2024-08-20	68	168
6230	18:40:00	20:20:00	2024-08-27	68	168
6231	18:40:00	20:20:00	2024-09-03	68	168
6232	18:40:00	20:20:00	2024-09-10	68	168
6233	18:40:00	20:20:00	2024-09-17	68	168
6234	18:40:00	20:20:00	2024-09-24	68	168
6235	18:40:00	20:20:00	2024-10-01	68	168
6236	18:40:00	20:20:00	2024-10-08	68	168
6237	18:40:00	20:20:00	2024-10-15	68	168
6238	18:40:00	20:20:00	2024-10-22	68	168
6239	18:40:00	20:20:00	2024-10-29	68	168
6240	18:40:00	20:20:00	2024-11-05	68	168
6241	18:40:00	20:20:00	2024-11-12	68	168
6242	18:40:00	20:20:00	2024-11-19	68	168
6243	18:40:00	20:20:00	2024-11-26	68	168
6244	18:40:00	20:20:00	2024-12-03	68	168
6245	18:40:00	20:20:00	2024-12-10	68	168
6246	08:30:00	10:10:00	2024-08-10	68	169
6247	08:30:00	10:10:00	2024-08-17	68	169
6248	08:30:00	10:10:00	2024-08-24	68	169
6249	08:30:00	10:10:00	2024-08-31	68	169
6250	08:30:00	10:10:00	2024-09-07	68	169
6251	08:30:00	10:10:00	2024-09-14	68	169
6252	08:30:00	10:10:00	2024-09-21	68	169
6253	08:30:00	10:10:00	2024-09-28	68	169
6254	08:30:00	10:10:00	2024-10-05	68	169
6255	08:30:00	10:10:00	2024-10-12	68	169
6256	08:30:00	10:10:00	2024-10-19	68	169
6257	08:30:00	10:10:00	2024-10-26	68	169
6258	08:30:00	10:10:00	2024-11-02	68	169
6259	08:30:00	10:10:00	2024-11-09	68	169
6260	08:30:00	10:10:00	2024-11-16	68	169
6261	08:30:00	10:10:00	2024-11-23	68	169
6262	08:30:00	10:10:00	2024-11-30	68	169
6263	08:30:00	10:10:00	2024-12-07	68	169
6264	09:20:00	11:00:00	2024-08-07	30	179
6265	09:20:00	11:00:00	2024-08-14	30	179
6266	09:20:00	11:00:00	2024-08-21	30	179
6267	09:20:00	11:00:00	2024-08-28	30	179
6268	09:20:00	11:00:00	2024-09-04	30	179
6269	09:20:00	11:00:00	2024-09-11	30	179
6270	09:20:00	11:00:00	2024-09-18	30	179
6271	09:20:00	11:00:00	2024-09-25	30	179
6272	09:20:00	11:00:00	2024-10-02	30	179
6273	09:20:00	11:00:00	2024-10-09	30	179
6274	09:20:00	11:00:00	2024-10-16	30	179
6275	09:20:00	11:00:00	2024-10-23	30	179
6276	09:20:00	11:00:00	2024-10-30	30	179
6277	09:20:00	11:00:00	2024-11-06	30	179
6278	09:20:00	11:00:00	2024-11-13	30	179
6279	09:20:00	11:00:00	2024-11-20	30	179
6280	09:20:00	11:00:00	2024-11-27	30	179
6281	09:20:00	11:00:00	2024-12-04	30	179
6282	09:20:00	11:00:00	2024-12-11	30	179
6283	13:10:00	14:50:00	2024-08-09	30	180
6284	13:10:00	14:50:00	2024-08-16	30	180
6285	13:10:00	14:50:00	2024-08-23	30	180
6286	13:10:00	14:50:00	2024-08-30	30	180
6287	13:10:00	14:50:00	2024-09-06	30	180
6288	13:10:00	14:50:00	2024-09-13	30	180
6289	13:10:00	14:50:00	2024-09-20	30	180
6290	13:10:00	14:50:00	2024-09-27	30	180
6291	13:10:00	14:50:00	2024-10-04	30	180
6292	13:10:00	14:50:00	2024-10-11	30	180
6293	13:10:00	14:50:00	2024-10-18	30	180
6294	13:10:00	14:50:00	2024-10-25	30	180
6295	13:10:00	14:50:00	2024-11-01	30	180
6296	13:10:00	14:50:00	2024-11-08	30	180
6297	13:10:00	14:50:00	2024-11-15	30	180
6298	13:10:00	14:50:00	2024-11-22	30	180
6299	13:10:00	14:50:00	2024-11-29	30	180
6300	13:10:00	14:50:00	2024-12-06	30	180
6301	09:20:00	11:00:00	2024-08-07	31	181
6302	09:20:00	11:00:00	2024-08-14	31	181
6303	09:20:00	11:00:00	2024-08-21	31	181
6304	09:20:00	11:00:00	2024-08-28	31	181
6305	09:20:00	11:00:00	2024-09-04	31	181
6306	09:20:00	11:00:00	2024-09-11	31	181
6307	09:20:00	11:00:00	2024-09-18	31	181
6308	09:20:00	11:00:00	2024-09-25	31	181
6309	09:20:00	11:00:00	2024-10-02	31	181
6310	09:20:00	11:00:00	2024-10-09	31	181
6311	09:20:00	11:00:00	2024-10-16	31	181
6312	09:20:00	11:00:00	2024-10-23	31	181
6313	09:20:00	11:00:00	2024-10-30	31	181
6314	09:20:00	11:00:00	2024-11-06	31	181
6315	09:20:00	11:00:00	2024-11-13	31	181
6316	09:20:00	11:00:00	2024-11-20	31	181
6317	09:20:00	11:00:00	2024-11-27	31	181
6318	09:20:00	11:00:00	2024-12-04	31	181
6319	09:20:00	11:00:00	2024-12-11	31	181
6320	13:10:00	14:50:00	2024-08-09	31	182
6321	13:10:00	14:50:00	2024-08-16	31	182
6322	13:10:00	14:50:00	2024-08-23	31	182
6323	13:10:00	14:50:00	2024-08-30	31	182
6324	13:10:00	14:50:00	2024-09-06	31	182
6325	13:10:00	14:50:00	2024-09-13	31	182
6326	13:10:00	14:50:00	2024-09-20	31	182
6327	13:10:00	14:50:00	2024-09-27	31	182
6328	13:10:00	14:50:00	2024-10-04	31	182
6329	13:10:00	14:50:00	2024-10-11	31	182
6330	13:10:00	14:50:00	2024-10-18	31	182
6331	13:10:00	14:50:00	2024-10-25	31	182
6332	13:10:00	14:50:00	2024-11-01	31	182
6333	13:10:00	14:50:00	2024-11-08	31	182
6334	13:10:00	14:50:00	2024-11-15	31	182
6335	13:10:00	14:50:00	2024-11-22	31	182
6336	13:10:00	14:50:00	2024-11-29	31	182
6337	13:10:00	14:50:00	2024-12-06	31	182
6507	13:10:00	14:50:00	2024-08-07	38	192
6508	13:10:00	14:50:00	2024-08-14	38	192
6509	13:10:00	14:50:00	2024-08-21	38	192
6510	13:10:00	14:50:00	2024-08-28	38	192
6511	13:10:00	14:50:00	2024-09-04	38	192
6512	13:10:00	14:50:00	2024-09-11	38	192
6513	13:10:00	14:50:00	2024-09-18	38	192
6514	13:10:00	14:50:00	2024-09-25	38	192
6515	13:10:00	14:50:00	2024-10-02	38	192
6516	13:10:00	14:50:00	2024-10-09	38	192
6517	13:10:00	14:50:00	2024-10-16	38	192
6518	13:10:00	14:50:00	2024-10-23	38	192
6519	13:10:00	14:50:00	2024-10-30	38	192
6520	13:10:00	14:50:00	2024-11-06	38	192
6521	13:10:00	14:50:00	2024-11-13	38	192
6522	13:10:00	14:50:00	2024-11-20	38	192
6523	13:10:00	14:50:00	2024-11-27	38	192
6524	13:10:00	14:50:00	2024-12-04	38	192
6525	13:10:00	14:50:00	2024-12-11	38	192
6526	13:10:00	14:50:00	2024-08-09	65	193
6527	13:10:00	14:50:00	2024-08-16	65	193
6528	13:10:00	14:50:00	2024-08-23	65	193
6529	13:10:00	14:50:00	2024-08-30	65	193
6530	13:10:00	14:50:00	2024-09-06	65	193
6531	13:10:00	14:50:00	2024-09-13	65	193
6532	13:10:00	14:50:00	2024-09-20	65	193
6533	13:10:00	14:50:00	2024-09-27	65	193
6534	13:10:00	14:50:00	2024-10-04	65	193
6535	13:10:00	14:50:00	2024-10-11	65	193
6536	13:10:00	14:50:00	2024-10-18	65	193
6537	13:10:00	14:50:00	2024-10-25	65	193
6538	13:10:00	14:50:00	2024-11-01	65	193
6539	13:10:00	14:50:00	2024-11-08	65	193
6540	13:10:00	14:50:00	2024-11-15	65	193
6541	13:10:00	14:50:00	2024-11-22	65	193
6542	13:10:00	14:50:00	2024-11-29	65	193
6543	13:10:00	14:50:00	2024-12-06	65	193
6581	13:10:00	14:50:00	2024-08-05	30	200
6582	13:10:00	14:50:00	2024-08-12	30	200
6583	13:10:00	14:50:00	2024-08-19	30	200
6584	13:10:00	14:50:00	2024-08-26	30	200
6585	13:10:00	14:50:00	2024-09-02	30	200
6586	13:10:00	14:50:00	2024-09-09	30	200
6587	13:10:00	14:50:00	2024-09-16	30	200
6588	13:10:00	14:50:00	2024-09-23	30	200
6589	13:10:00	14:50:00	2024-09-30	30	200
6590	13:10:00	14:50:00	2024-10-07	30	200
6591	13:10:00	14:50:00	2024-10-14	30	200
6592	13:10:00	14:50:00	2024-10-21	30	200
6593	13:10:00	14:50:00	2024-10-28	30	200
6594	13:10:00	14:50:00	2024-11-04	30	200
6595	13:10:00	14:50:00	2024-11-11	30	200
6596	13:10:00	14:50:00	2024-11-18	30	200
6597	13:10:00	14:50:00	2024-11-25	30	200
6598	13:10:00	14:50:00	2024-12-02	30	200
6599	13:10:00	14:50:00	2024-12-09	30	200
6600	15:00:00	16:40:00	2024-08-07	30	201
6601	15:00:00	16:40:00	2024-08-14	30	201
6602	15:00:00	16:40:00	2024-08-21	30	201
6603	15:00:00	16:40:00	2024-08-28	30	201
6604	15:00:00	16:40:00	2024-09-04	30	201
6605	15:00:00	16:40:00	2024-09-11	30	201
6606	15:00:00	16:40:00	2024-09-18	30	201
6607	15:00:00	16:40:00	2024-09-25	30	201
6608	15:00:00	16:40:00	2024-10-02	30	201
6609	15:00:00	16:40:00	2024-10-09	30	201
6610	15:00:00	16:40:00	2024-10-16	30	201
6611	15:00:00	16:40:00	2024-10-23	30	201
6612	15:00:00	16:40:00	2024-10-30	30	201
6613	15:00:00	16:40:00	2024-11-06	30	201
6614	15:00:00	16:40:00	2024-11-13	30	201
6615	15:00:00	16:40:00	2024-11-20	30	201
6616	15:00:00	16:40:00	2024-11-27	30	201
6617	15:00:00	16:40:00	2024-12-04	30	201
6618	15:00:00	16:40:00	2024-12-11	30	201
6338	09:20:00	11:00:00	2024-08-07	33	183
6339	09:20:00	11:00:00	2024-08-14	33	183
6340	09:20:00	11:00:00	2024-08-21	33	183
6341	09:20:00	11:00:00	2024-08-28	33	183
6342	09:20:00	11:00:00	2024-09-04	33	183
6343	09:20:00	11:00:00	2024-09-11	33	183
6344	09:20:00	11:00:00	2024-09-18	33	183
6345	09:20:00	11:00:00	2024-09-25	33	183
6346	09:20:00	11:00:00	2024-10-02	33	183
6347	09:20:00	11:00:00	2024-10-09	33	183
6348	09:20:00	11:00:00	2024-10-16	33	183
6349	09:20:00	11:00:00	2024-10-23	33	183
6350	09:20:00	11:00:00	2024-10-30	33	183
6351	09:20:00	11:00:00	2024-11-06	33	183
6352	09:20:00	11:00:00	2024-11-13	33	183
6353	09:20:00	11:00:00	2024-11-20	33	183
6354	09:20:00	11:00:00	2024-11-27	33	183
6355	09:20:00	11:00:00	2024-12-04	33	183
6356	09:20:00	11:00:00	2024-12-11	33	183
6357	13:10:00	14:50:00	2024-08-09	33	184
6358	13:10:00	14:50:00	2024-08-16	33	184
6359	13:10:00	14:50:00	2024-08-23	33	184
6360	13:10:00	14:50:00	2024-08-30	33	184
6361	13:10:00	14:50:00	2024-09-06	33	184
6362	13:10:00	14:50:00	2024-09-13	33	184
6363	13:10:00	14:50:00	2024-09-20	33	184
6364	13:10:00	14:50:00	2024-09-27	33	184
6365	13:10:00	14:50:00	2024-10-04	33	184
6366	13:10:00	14:50:00	2024-10-11	33	184
6367	13:10:00	14:50:00	2024-10-18	33	184
6368	13:10:00	14:50:00	2024-10-25	33	184
6369	13:10:00	14:50:00	2024-11-01	33	184
6370	13:10:00	14:50:00	2024-11-08	33	184
6371	13:10:00	14:50:00	2024-11-15	33	184
6372	13:10:00	14:50:00	2024-11-22	33	184
6373	13:10:00	14:50:00	2024-11-29	33	184
6374	13:10:00	14:50:00	2024-12-06	33	184
6375	13:10:00	15:50:00	2024-08-05	29	185
6376	13:10:00	15:50:00	2024-08-12	29	185
6377	13:10:00	15:50:00	2024-08-19	29	185
6378	13:10:00	15:50:00	2024-08-26	29	185
6379	13:10:00	15:50:00	2024-09-02	29	185
6380	13:10:00	15:50:00	2024-09-09	29	185
6381	13:10:00	15:50:00	2024-09-16	29	185
6382	13:10:00	15:50:00	2024-09-23	29	185
6383	13:10:00	15:50:00	2024-09-30	29	185
6384	13:10:00	15:50:00	2024-10-07	29	185
6385	13:10:00	15:50:00	2024-10-14	29	185
6386	13:10:00	15:50:00	2024-10-21	29	185
6387	13:10:00	15:50:00	2024-10-28	29	185
6388	13:10:00	15:50:00	2024-11-04	29	185
6389	13:10:00	15:50:00	2024-11-11	29	185
6390	13:10:00	15:50:00	2024-11-18	29	185
6391	13:10:00	15:50:00	2024-11-25	29	185
6392	13:10:00	15:50:00	2024-12-02	29	185
6393	13:10:00	15:50:00	2024-12-09	29	185
6394	13:10:00	15:50:00	2024-08-08	29	186
6395	13:10:00	15:50:00	2024-08-15	29	186
6396	13:10:00	15:50:00	2024-08-22	29	186
6397	13:10:00	15:50:00	2024-08-29	29	186
6398	13:10:00	15:50:00	2024-09-05	29	186
6399	13:10:00	15:50:00	2024-09-12	29	186
6400	13:10:00	15:50:00	2024-09-19	29	186
6401	13:10:00	15:50:00	2024-09-26	29	186
6402	13:10:00	15:50:00	2024-10-03	29	186
6403	13:10:00	15:50:00	2024-10-10	29	186
6404	13:10:00	15:50:00	2024-10-17	29	186
6405	13:10:00	15:50:00	2024-10-24	29	186
6406	13:10:00	15:50:00	2024-10-31	29	186
6407	13:10:00	15:50:00	2024-11-07	29	186
6408	13:10:00	15:50:00	2024-11-14	29	186
6409	13:10:00	15:50:00	2024-11-21	29	186
6410	13:10:00	15:50:00	2024-11-28	29	186
6411	13:10:00	15:50:00	2024-12-05	29	186
6412	13:10:00	15:50:00	2024-12-12	29	186
6413	08:20:00	11:00:00	2024-08-08	29	187
6414	08:20:00	11:00:00	2024-08-15	29	187
6415	08:20:00	11:00:00	2024-08-22	29	187
6416	08:20:00	11:00:00	2024-08-29	29	187
6417	08:20:00	11:00:00	2024-09-05	29	187
6418	08:20:00	11:00:00	2024-09-12	29	187
6419	08:20:00	11:00:00	2024-09-19	29	187
6420	08:20:00	11:00:00	2024-09-26	29	187
6421	08:20:00	11:00:00	2024-10-03	29	187
6422	08:20:00	11:00:00	2024-10-10	29	187
6423	08:20:00	11:00:00	2024-10-17	29	187
6424	08:20:00	11:00:00	2024-10-24	29	187
6425	08:20:00	11:00:00	2024-10-31	29	187
6426	08:20:00	11:00:00	2024-11-07	29	187
6427	08:20:00	11:00:00	2024-11-14	29	187
6428	08:20:00	11:00:00	2024-11-21	29	187
6429	08:20:00	11:00:00	2024-11-28	29	187
6430	08:20:00	11:00:00	2024-12-05	29	187
6431	08:20:00	11:00:00	2024-12-12	29	187
6432	13:10:00	15:50:00	2024-08-07	29	188
6433	13:10:00	15:50:00	2024-08-14	29	188
6434	13:10:00	15:50:00	2024-08-21	29	188
6435	13:10:00	15:50:00	2024-08-28	29	188
6436	13:10:00	15:50:00	2024-09-04	29	188
6437	13:10:00	15:50:00	2024-09-11	29	188
6438	13:10:00	15:50:00	2024-09-18	29	188
6439	13:10:00	15:50:00	2024-09-25	29	188
6440	13:10:00	15:50:00	2024-10-02	29	188
6441	13:10:00	15:50:00	2024-10-09	29	188
6442	13:10:00	15:50:00	2024-10-16	29	188
6443	13:10:00	15:50:00	2024-10-23	29	188
6444	13:10:00	15:50:00	2024-10-30	29	188
6445	13:10:00	15:50:00	2024-11-06	29	188
6446	13:10:00	15:50:00	2024-11-13	29	188
6447	13:10:00	15:50:00	2024-11-20	29	188
6448	13:10:00	15:50:00	2024-11-27	29	188
6449	13:10:00	15:50:00	2024-12-04	29	188
6450	13:10:00	15:50:00	2024-12-11	29	188
6451	08:20:00	11:00:00	2024-08-05	29	189
6452	08:20:00	11:00:00	2024-08-12	29	189
6453	08:20:00	11:00:00	2024-08-19	29	189
6454	08:20:00	11:00:00	2024-08-26	29	189
6455	08:20:00	11:00:00	2024-09-02	29	189
6456	08:20:00	11:00:00	2024-09-09	29	189
6457	08:20:00	11:00:00	2024-09-16	29	189
6458	08:20:00	11:00:00	2024-09-23	29	189
6459	08:20:00	11:00:00	2024-09-30	29	189
6460	08:20:00	11:00:00	2024-10-07	29	189
6461	08:20:00	11:00:00	2024-10-14	29	189
6462	08:20:00	11:00:00	2024-10-21	29	189
6463	08:20:00	11:00:00	2024-10-28	29	189
6464	08:20:00	11:00:00	2024-11-04	29	189
6465	08:20:00	11:00:00	2024-11-11	29	189
6466	08:20:00	11:00:00	2024-11-18	29	189
6467	08:20:00	11:00:00	2024-11-25	29	189
6468	08:20:00	11:00:00	2024-12-02	29	189
6469	08:20:00	11:00:00	2024-12-09	29	189
6470	13:10:00	15:50:00	2024-08-06	29	190
6471	13:10:00	15:50:00	2024-08-13	29	190
6472	13:10:00	15:50:00	2024-08-20	29	190
6473	13:10:00	15:50:00	2024-08-27	29	190
6474	13:10:00	15:50:00	2024-09-03	29	190
6475	13:10:00	15:50:00	2024-09-10	29	190
6476	13:10:00	15:50:00	2024-09-17	29	190
6477	13:10:00	15:50:00	2024-09-24	29	190
6478	13:10:00	15:50:00	2024-10-01	29	190
6479	13:10:00	15:50:00	2024-10-08	29	190
6480	13:10:00	15:50:00	2024-10-15	29	190
6481	13:10:00	15:50:00	2024-10-22	29	190
6482	13:10:00	15:50:00	2024-10-29	29	190
6483	13:10:00	15:50:00	2024-11-05	29	190
6484	13:10:00	15:50:00	2024-11-12	29	190
6485	13:10:00	15:50:00	2024-11-19	29	190
6486	13:10:00	15:50:00	2024-11-26	29	190
6487	13:10:00	15:50:00	2024-12-03	29	190
6488	13:10:00	15:50:00	2024-12-10	29	190
6489	15:00:00	17:30:00	2024-08-09	29	191
6490	15:00:00	17:30:00	2024-08-16	29	191
6491	15:00:00	17:30:00	2024-08-23	29	191
6492	15:00:00	17:30:00	2024-08-30	29	191
6493	15:00:00	17:30:00	2024-09-06	29	191
6494	15:00:00	17:30:00	2024-09-13	29	191
6495	15:00:00	17:30:00	2024-09-20	29	191
6496	15:00:00	17:30:00	2024-09-27	29	191
6497	15:00:00	17:30:00	2024-10-04	29	191
6498	15:00:00	17:30:00	2024-10-11	29	191
6499	15:00:00	17:30:00	2024-10-18	29	191
6500	15:00:00	17:30:00	2024-10-25	29	191
6501	15:00:00	17:30:00	2024-11-01	29	191
6502	15:00:00	17:30:00	2024-11-08	29	191
6503	15:00:00	17:30:00	2024-11-15	29	191
6504	15:00:00	17:30:00	2024-11-22	29	191
6505	15:00:00	17:30:00	2024-11-29	29	191
6506	15:00:00	17:30:00	2024-12-06	29	191
6544	13:10:00	14:50:00	2024-08-07	22	194
6545	13:10:00	14:50:00	2024-08-14	22	194
6546	13:10:00	14:50:00	2024-08-21	22	194
6547	13:10:00	14:50:00	2024-08-28	22	194
6548	13:10:00	14:50:00	2024-09-04	22	194
6549	13:10:00	14:50:00	2024-09-11	22	194
6550	13:10:00	14:50:00	2024-09-18	22	194
6551	13:10:00	14:50:00	2024-09-25	22	194
6552	13:10:00	14:50:00	2024-10-02	22	194
6553	13:10:00	14:50:00	2024-10-09	22	194
6554	13:10:00	14:50:00	2024-10-16	22	194
6555	13:10:00	14:50:00	2024-10-23	22	194
6556	13:10:00	14:50:00	2024-10-30	22	194
6557	13:10:00	14:50:00	2024-11-06	22	194
6558	13:10:00	14:50:00	2024-11-13	22	194
6559	13:10:00	14:50:00	2024-11-20	22	194
6560	13:10:00	14:50:00	2024-11-27	22	194
6561	13:10:00	14:50:00	2024-12-04	22	194
6562	13:10:00	14:50:00	2024-12-11	22	194
6563	13:10:00	14:50:00	2024-08-09	21	195
6564	13:10:00	14:50:00	2024-08-16	21	195
6565	13:10:00	14:50:00	2024-08-23	21	195
6566	13:10:00	14:50:00	2024-08-30	21	195
6567	13:10:00	14:50:00	2024-09-06	21	195
6568	13:10:00	14:50:00	2024-09-13	21	195
6569	13:10:00	14:50:00	2024-09-20	21	195
6570	13:10:00	14:50:00	2024-09-27	21	195
6571	13:10:00	14:50:00	2024-10-04	21	195
6572	13:10:00	14:50:00	2024-10-11	21	195
6573	13:10:00	14:50:00	2024-10-18	21	195
6574	13:10:00	14:50:00	2024-10-25	21	195
6575	13:10:00	14:50:00	2024-11-01	21	195
6576	13:10:00	14:50:00	2024-11-08	21	195
6577	13:10:00	14:50:00	2024-11-15	21	195
6578	13:10:00	14:50:00	2024-11-22	21	195
6579	13:10:00	14:50:00	2024-11-29	21	195
6580	13:10:00	14:50:00	2024-12-06	21	195
6619	09:20:00	11:00:00	2024-05-09	30	14
6620	09:20:00	11:00:00	2024-05-16	30	14
6621	09:20:00	11:00:00	2024-05-23	30	14
6622	09:20:00	11:00:00	2024-05-30	30	14
6623	09:20:00	11:00:00	2024-06-06	30	14
6624	09:20:00	11:00:00	2024-06-13	30	14
6625	09:20:00	11:00:00	2024-06-20	30	14
6626	09:20:00	11:00:00	2024-06-27	30	14
6627	09:20:00	11:00:00	2024-07-04	30	14
6628	09:20:00	11:00:00	2024-07-11	30	14
6629	09:20:00	11:00:00	2024-07-18	30	14
6630	09:20:00	11:00:00	2024-07-25	30	14
6631	09:20:00	11:00:00	2024-08-01	30	14
6632	09:20:00	11:00:00	2024-08-08	30	14
6633	09:20:00	11:00:00	2024-08-15	30	14
6634	13:10:00	16:40:00	2024-05-08	67	10
6635	13:10:00	16:40:00	2024-05-15	67	10
6636	13:10:00	16:40:00	2024-05-22	67	10
6637	13:10:00	16:40:00	2024-05-29	67	10
6638	13:10:00	16:40:00	2024-06-05	67	10
6639	13:10:00	16:40:00	2024-06-12	67	10
6640	13:10:00	16:40:00	2024-06-19	67	10
6641	13:10:00	16:40:00	2024-06-26	67	10
6642	13:10:00	16:40:00	2024-07-03	67	10
6643	13:10:00	16:40:00	2024-07-10	67	10
6644	13:10:00	16:40:00	2024-07-17	67	10
6645	13:10:00	16:40:00	2024-07-24	67	10
6646	13:10:00	16:40:00	2024-07-31	67	10
6647	13:10:00	16:40:00	2024-08-07	67	10
6648	13:10:00	16:40:00	2024-08-14	67	10
6649	13:10:00	14:50:00	2024-08-05	31	202
6650	13:10:00	14:50:00	2024-08-12	31	202
6651	13:10:00	14:50:00	2024-08-19	31	202
6652	13:10:00	14:50:00	2024-08-26	31	202
6653	13:10:00	14:50:00	2024-09-02	31	202
6654	13:10:00	14:50:00	2024-09-09	31	202
6655	13:10:00	14:50:00	2024-09-16	31	202
6656	13:10:00	14:50:00	2024-09-23	31	202
6657	13:10:00	14:50:00	2024-09-30	31	202
6658	13:10:00	14:50:00	2024-10-07	31	202
6659	13:10:00	14:50:00	2024-10-14	31	202
6660	13:10:00	14:50:00	2024-10-21	31	202
6661	13:10:00	14:50:00	2024-10-28	31	202
6662	13:10:00	14:50:00	2024-11-04	31	202
6663	13:10:00	14:50:00	2024-11-11	31	202
6664	13:10:00	14:50:00	2024-11-18	31	202
6665	13:10:00	14:50:00	2024-11-25	31	202
6666	13:10:00	14:50:00	2024-12-02	31	202
6667	13:10:00	14:50:00	2024-12-09	31	202
6668	15:00:00	16:40:00	2024-08-07	31	203
6669	15:00:00	16:40:00	2024-08-14	31	203
6670	15:00:00	16:40:00	2024-08-21	31	203
6671	15:00:00	16:40:00	2024-08-28	31	203
6672	15:00:00	16:40:00	2024-09-04	31	203
6673	15:00:00	16:40:00	2024-09-11	31	203
6674	15:00:00	16:40:00	2024-09-18	31	203
6675	15:00:00	16:40:00	2024-09-25	31	203
6676	15:00:00	16:40:00	2024-10-02	31	203
6677	15:00:00	16:40:00	2024-10-09	31	203
6678	15:00:00	16:40:00	2024-10-16	31	203
6679	15:00:00	16:40:00	2024-10-23	31	203
6680	15:00:00	16:40:00	2024-10-30	31	203
6681	15:00:00	16:40:00	2024-11-06	31	203
6682	15:00:00	16:40:00	2024-11-13	31	203
6683	15:00:00	16:40:00	2024-11-20	31	203
6684	15:00:00	16:40:00	2024-11-27	31	203
6685	15:00:00	16:40:00	2024-12-04	31	203
6686	15:00:00	16:40:00	2024-12-11	31	203
6687	13:10:00	14:50:00	2024-08-05	33	204
6688	13:10:00	14:50:00	2024-08-12	33	204
6689	13:10:00	14:50:00	2024-08-19	33	204
6690	13:10:00	14:50:00	2024-08-26	33	204
6691	13:10:00	14:50:00	2024-09-02	33	204
6692	13:10:00	14:50:00	2024-09-09	33	204
6693	13:10:00	14:50:00	2024-09-16	33	204
6694	13:10:00	14:50:00	2024-09-23	33	204
6695	13:10:00	14:50:00	2024-09-30	33	204
6696	13:10:00	14:50:00	2024-10-07	33	204
6697	13:10:00	14:50:00	2024-10-14	33	204
6698	13:10:00	14:50:00	2024-10-21	33	204
6699	13:10:00	14:50:00	2024-10-28	33	204
6700	13:10:00	14:50:00	2024-11-04	33	204
6701	13:10:00	14:50:00	2024-11-11	33	204
6702	13:10:00	14:50:00	2024-11-18	33	204
6703	13:10:00	14:50:00	2024-11-25	33	204
6704	13:10:00	14:50:00	2024-12-02	33	204
6705	13:10:00	14:50:00	2024-12-09	33	204
6706	15:00:00	16:40:00	2024-08-07	33	205
6707	15:00:00	16:40:00	2024-08-14	33	205
6708	15:00:00	16:40:00	2024-08-21	33	205
6709	15:00:00	16:40:00	2024-08-28	33	205
6710	15:00:00	16:40:00	2024-09-04	33	205
6711	15:00:00	16:40:00	2024-09-11	33	205
6712	15:00:00	16:40:00	2024-09-18	33	205
6713	15:00:00	16:40:00	2024-09-25	33	205
6714	15:00:00	16:40:00	2024-10-02	33	205
6715	15:00:00	16:40:00	2024-10-09	33	205
6716	15:00:00	16:40:00	2024-10-16	33	205
6717	15:00:00	16:40:00	2024-10-23	33	205
6718	15:00:00	16:40:00	2024-10-30	33	205
6719	15:00:00	16:40:00	2024-11-06	33	205
6720	15:00:00	16:40:00	2024-11-13	33	205
6721	15:00:00	16:40:00	2024-11-20	33	205
6722	15:00:00	16:40:00	2024-11-27	33	205
6723	15:00:00	16:40:00	2024-12-04	33	205
6724	15:00:00	16:40:00	2024-12-11	33	205
6725	12:00:00	12:50:00	2024-08-10	68	211
6726	12:00:00	12:50:00	2024-08-17	68	211
6727	12:00:00	12:50:00	2024-08-24	68	211
6728	12:00:00	12:50:00	2024-08-31	68	211
6729	12:00:00	12:50:00	2024-09-07	68	211
6730	12:00:00	12:50:00	2024-09-14	68	211
6731	12:00:00	12:50:00	2024-09-21	68	211
6732	12:00:00	12:50:00	2024-09-28	68	211
6733	12:00:00	12:50:00	2024-10-05	68	211
6734	12:00:00	12:50:00	2024-10-12	68	211
6735	12:00:00	12:50:00	2024-10-19	68	211
6736	12:00:00	12:50:00	2024-10-26	68	211
6737	12:00:00	12:50:00	2024-11-02	68	211
6738	12:00:00	12:50:00	2024-11-09	68	211
6739	12:00:00	12:50:00	2024-11-16	68	211
6740	12:00:00	12:50:00	2024-11-23	68	211
6741	12:00:00	12:50:00	2024-11-30	68	211
6742	12:00:00	12:50:00	2024-12-07	68	211
6743	13:10:00	14:00:00	2024-08-10	68	212
6744	13:10:00	14:00:00	2024-08-17	68	212
6745	13:10:00	14:00:00	2024-08-24	68	212
6746	13:10:00	14:00:00	2024-08-31	68	212
6747	13:10:00	14:00:00	2024-09-07	68	212
6748	13:10:00	14:00:00	2024-09-14	68	212
6749	13:10:00	14:00:00	2024-09-21	68	212
6750	13:10:00	14:00:00	2024-09-28	68	212
6751	13:10:00	14:00:00	2024-10-05	68	212
6752	13:10:00	14:00:00	2024-10-12	68	212
6753	13:10:00	14:00:00	2024-10-19	68	212
6754	13:10:00	14:00:00	2024-10-26	68	212
6755	13:10:00	14:00:00	2024-11-02	68	212
6756	13:10:00	14:00:00	2024-11-09	68	212
6757	13:10:00	14:00:00	2024-11-16	68	212
6758	13:10:00	14:00:00	2024-11-23	68	212
6759	13:10:00	14:00:00	2024-11-30	68	212
6760	13:10:00	14:00:00	2024-12-07	68	212
6761	09:10:00	10:00:00	2024-08-10	68	213
6762	09:10:00	10:00:00	2024-08-17	68	213
6763	09:10:00	10:00:00	2024-08-24	68	213
6764	09:10:00	10:00:00	2024-08-31	68	213
6765	09:10:00	10:00:00	2024-09-07	68	213
6766	09:10:00	10:00:00	2024-09-14	68	213
6767	09:10:00	10:00:00	2024-09-21	68	213
6768	09:10:00	10:00:00	2024-09-28	68	213
6769	09:10:00	10:00:00	2024-10-05	68	213
6770	09:10:00	10:00:00	2024-10-12	68	213
6771	09:10:00	10:00:00	2024-10-19	68	213
6772	09:10:00	10:00:00	2024-10-26	68	213
6773	09:10:00	10:00:00	2024-11-02	68	213
6774	09:10:00	10:00:00	2024-11-09	68	213
6775	09:10:00	10:00:00	2024-11-16	68	213
6776	09:10:00	10:00:00	2024-11-23	68	213
6777	09:10:00	10:00:00	2024-11-30	68	213
6778	09:10:00	10:00:00	2024-12-07	68	213
6779	08:20:00	12:00:00	2024-08-08	75	214
6780	08:20:00	12:00:00	2024-08-15	75	214
6781	08:20:00	12:00:00	2024-08-22	75	214
6782	08:20:00	12:00:00	2024-08-29	75	214
6783	08:20:00	12:00:00	2024-09-05	75	214
6784	08:20:00	12:00:00	2024-09-12	75	214
6785	08:20:00	12:00:00	2024-09-19	75	214
6786	08:20:00	12:00:00	2024-09-26	75	214
6787	08:20:00	12:00:00	2024-10-03	75	214
6788	08:20:00	12:00:00	2024-10-10	75	214
6789	08:20:00	12:00:00	2024-10-17	75	214
6790	08:20:00	12:00:00	2024-10-24	75	214
6791	08:20:00	12:00:00	2024-10-31	75	214
6792	08:20:00	12:00:00	2024-11-07	75	214
6793	08:20:00	12:00:00	2024-11-14	75	214
6794	08:20:00	12:00:00	2024-11-21	75	214
6795	08:20:00	12:00:00	2024-11-28	75	214
6796	08:20:00	12:00:00	2024-12-05	75	214
6797	08:20:00	12:00:00	2024-12-12	75	214
6798	08:20:00	12:00:00	2024-08-06	75	215
6799	08:20:00	12:00:00	2024-08-13	75	215
6800	08:20:00	12:00:00	2024-08-20	75	215
6801	08:20:00	12:00:00	2024-08-27	75	215
6802	08:20:00	12:00:00	2024-09-03	75	215
6803	08:20:00	12:00:00	2024-09-10	75	215
6804	08:20:00	12:00:00	2024-09-17	75	215
6805	08:20:00	12:00:00	2024-09-24	75	215
6806	08:20:00	12:00:00	2024-10-01	75	215
6807	08:20:00	12:00:00	2024-10-08	75	215
6808	08:20:00	12:00:00	2024-10-15	75	215
6809	08:20:00	12:00:00	2024-10-22	75	215
6810	08:20:00	12:00:00	2024-10-29	75	215
6811	08:20:00	12:00:00	2024-11-05	75	215
6812	08:20:00	12:00:00	2024-11-12	75	215
6813	08:20:00	12:00:00	2024-11-19	75	215
6814	08:20:00	12:00:00	2024-11-26	75	215
6815	08:20:00	12:00:00	2024-12-03	75	215
6816	08:20:00	12:00:00	2024-12-10	75	215
6817	08:20:00	12:00:00	2024-08-07	27	216
6818	08:20:00	12:00:00	2024-08-14	27	216
6819	08:20:00	12:00:00	2024-08-21	27	216
6820	08:20:00	12:00:00	2024-08-28	27	216
6821	08:20:00	12:00:00	2024-09-04	27	216
6822	08:20:00	12:00:00	2024-09-11	27	216
6823	08:20:00	12:00:00	2024-09-18	27	216
6824	08:20:00	12:00:00	2024-09-25	27	216
6825	08:20:00	12:00:00	2024-10-02	27	216
6826	08:20:00	12:00:00	2024-10-09	27	216
6827	08:20:00	12:00:00	2024-10-16	27	216
6828	08:20:00	12:00:00	2024-10-23	27	216
6829	08:20:00	12:00:00	2024-10-30	27	216
6830	08:20:00	12:00:00	2024-11-06	27	216
6831	08:20:00	12:00:00	2024-11-13	27	216
6832	08:20:00	12:00:00	2024-11-20	27	216
6833	08:20:00	12:00:00	2024-11-27	27	216
6834	08:20:00	12:00:00	2024-12-04	27	216
6835	08:20:00	12:00:00	2024-12-11	27	216
6836	14:00:00	17:40:00	2024-08-08	75	217
6837	14:00:00	17:40:00	2024-08-15	75	217
6838	14:00:00	17:40:00	2024-08-22	75	217
6839	14:00:00	17:40:00	2024-08-29	75	217
6840	14:00:00	17:40:00	2024-09-05	75	217
6841	14:00:00	17:40:00	2024-09-12	75	217
6842	14:00:00	17:40:00	2024-09-19	75	217
6843	14:00:00	17:40:00	2024-09-26	75	217
6844	14:00:00	17:40:00	2024-10-03	75	217
6845	14:00:00	17:40:00	2024-10-10	75	217
6846	14:00:00	17:40:00	2024-10-17	75	217
6847	14:00:00	17:40:00	2024-10-24	75	217
6848	14:00:00	17:40:00	2024-10-31	75	217
6849	14:00:00	17:40:00	2024-11-07	75	217
6850	14:00:00	17:40:00	2024-11-14	75	217
6851	14:00:00	17:40:00	2024-11-21	75	217
6852	14:00:00	17:40:00	2024-11-28	75	217
6853	14:00:00	17:40:00	2024-12-05	75	217
6854	14:00:00	17:40:00	2024-12-12	75	217
6855	10:20:00	12:00:00	2024-05-06	23	218
6856	10:20:00	12:00:00	2024-05-13	23	218
6857	10:20:00	12:00:00	2024-05-20	23	218
6858	10:20:00	12:00:00	2024-05-27	23	218
6859	10:20:00	12:00:00	2024-06-03	23	218
6860	10:20:00	12:00:00	2024-06-10	23	218
6861	10:20:00	12:00:00	2024-06-17	23	218
6862	10:20:00	12:00:00	2024-06-24	23	218
6863	10:20:00	12:00:00	2024-07-01	23	218
6864	10:20:00	12:00:00	2024-07-08	23	218
6865	10:20:00	12:00:00	2024-07-15	23	218
6866	10:20:00	12:00:00	2024-07-22	23	218
6867	10:20:00	12:00:00	2024-07-29	23	218
6868	10:20:00	12:00:00	2024-08-05	23	218
6869	10:20:00	12:00:00	2024-08-12	23	218
6870	08:20:00	10:00:00	2024-05-08	23	219
6871	08:20:00	10:00:00	2024-05-15	23	219
6872	08:20:00	10:00:00	2024-05-22	23	219
6873	08:20:00	10:00:00	2024-05-29	23	219
6874	08:20:00	10:00:00	2024-06-05	23	219
6875	08:20:00	10:00:00	2024-06-12	23	219
6876	08:20:00	10:00:00	2024-06-19	23	219
6877	08:20:00	10:00:00	2024-06-26	23	219
6878	08:20:00	10:00:00	2024-07-03	23	219
6879	08:20:00	10:00:00	2024-07-10	23	219
6880	08:20:00	10:00:00	2024-07-17	23	219
6881	08:20:00	10:00:00	2024-07-24	23	219
6882	08:20:00	10:00:00	2024-07-31	23	219
6883	08:20:00	10:00:00	2024-08-07	23	219
6884	08:20:00	10:00:00	2024-08-14	23	219
6885	10:20:00	12:00:00	2024-05-06	25	220
6886	10:20:00	12:00:00	2024-05-13	25	220
6887	10:20:00	12:00:00	2024-05-20	25	220
6888	10:20:00	12:00:00	2024-05-27	25	220
6889	10:20:00	12:00:00	2024-06-03	25	220
6890	10:20:00	12:00:00	2024-06-10	25	220
6891	10:20:00	12:00:00	2024-06-17	25	220
6892	10:20:00	12:00:00	2024-06-24	25	220
6893	10:20:00	12:00:00	2024-07-01	25	220
6894	10:20:00	12:00:00	2024-07-08	25	220
6895	10:20:00	12:00:00	2024-07-15	25	220
6896	10:20:00	12:00:00	2024-07-22	25	220
6897	10:20:00	12:00:00	2024-07-29	25	220
6898	10:20:00	12:00:00	2024-08-05	25	220
6899	10:20:00	12:00:00	2024-08-12	25	220
6900	08:20:00	10:00:00	2024-05-08	25	221
6901	08:20:00	10:00:00	2024-05-15	25	221
6902	08:20:00	10:00:00	2024-05-22	25	221
6903	08:20:00	10:00:00	2024-05-29	25	221
6904	08:20:00	10:00:00	2024-06-05	25	221
6905	08:20:00	10:00:00	2024-06-12	25	221
6906	08:20:00	10:00:00	2024-06-19	25	221
6907	08:20:00	10:00:00	2024-06-26	25	221
6908	08:20:00	10:00:00	2024-07-03	25	221
6909	08:20:00	10:00:00	2024-07-10	25	221
6910	08:20:00	10:00:00	2024-07-17	25	221
6911	08:20:00	10:00:00	2024-07-24	25	221
6912	08:20:00	10:00:00	2024-07-31	25	221
6913	08:20:00	10:00:00	2024-08-07	25	221
6914	08:20:00	10:00:00	2024-08-14	25	221
6945	08:20:00	10:00:00	2024-05-06	25	224
6946	08:20:00	10:00:00	2024-05-13	25	224
6947	08:20:00	10:00:00	2024-05-20	25	224
6948	08:20:00	10:00:00	2024-05-27	25	224
6949	08:20:00	10:00:00	2024-06-03	25	224
6950	08:20:00	10:00:00	2024-06-10	25	224
6951	08:20:00	10:00:00	2024-06-17	25	224
6952	08:20:00	10:00:00	2024-06-24	25	224
6953	08:20:00	10:00:00	2024-07-01	25	224
6954	08:20:00	10:00:00	2024-07-08	25	224
6955	08:20:00	10:00:00	2024-07-15	25	224
6956	08:20:00	10:00:00	2024-07-22	25	224
6957	08:20:00	10:00:00	2024-07-29	25	224
6958	08:20:00	10:00:00	2024-08-05	25	224
6959	08:20:00	10:00:00	2024-08-12	25	224
6960	10:20:00	12:00:00	2024-05-08	25	225
6961	10:20:00	12:00:00	2024-05-15	25	225
6962	10:20:00	12:00:00	2024-05-22	25	225
6963	10:20:00	12:00:00	2024-05-29	25	225
6964	10:20:00	12:00:00	2024-06-05	25	225
6965	10:20:00	12:00:00	2024-06-12	25	225
6966	10:20:00	12:00:00	2024-06-19	25	225
6967	10:20:00	12:00:00	2024-06-26	25	225
6968	10:20:00	12:00:00	2024-07-03	25	225
6969	10:20:00	12:00:00	2024-07-10	25	225
6970	10:20:00	12:00:00	2024-07-17	25	225
6971	10:20:00	12:00:00	2024-07-24	25	225
6972	10:20:00	12:00:00	2024-07-31	25	225
6973	10:20:00	12:00:00	2024-08-07	25	225
6974	10:20:00	12:00:00	2024-08-14	25	225
6975	09:20:00	11:00:00	2024-08-06	30	235
6976	09:20:00	11:00:00	2024-08-13	30	235
6977	09:20:00	11:00:00	2024-08-20	30	235
6978	09:20:00	11:00:00	2024-08-27	30	235
6979	09:20:00	11:00:00	2024-09-03	30	235
6980	09:20:00	11:00:00	2024-09-10	30	235
6981	09:20:00	11:00:00	2024-09-17	30	235
6982	09:20:00	11:00:00	2024-09-24	30	235
6983	09:20:00	11:00:00	2024-10-01	30	235
6984	09:20:00	11:00:00	2024-10-08	30	235
6985	09:20:00	11:00:00	2024-10-15	30	235
6986	09:20:00	11:00:00	2024-10-22	30	235
6987	09:20:00	11:00:00	2024-10-29	30	235
6988	09:20:00	11:00:00	2024-11-05	30	235
6989	09:20:00	11:00:00	2024-11-12	30	235
6990	09:20:00	11:00:00	2024-11-19	30	235
6991	09:20:00	11:00:00	2024-11-26	30	235
6992	09:20:00	11:00:00	2024-12-03	30	235
6993	09:20:00	11:00:00	2024-12-10	30	235
6994	09:20:00	11:00:00	2024-08-06	31	236
6995	09:20:00	11:00:00	2024-08-13	31	236
6996	09:20:00	11:00:00	2024-08-20	31	236
6997	09:20:00	11:00:00	2024-08-27	31	236
6998	09:20:00	11:00:00	2024-09-03	31	236
6999	09:20:00	11:00:00	2024-09-10	31	236
7000	09:20:00	11:00:00	2024-09-17	31	236
7001	09:20:00	11:00:00	2024-09-24	31	236
7002	09:20:00	11:00:00	2024-10-01	31	236
7003	09:20:00	11:00:00	2024-10-08	31	236
7004	09:20:00	11:00:00	2024-10-15	31	236
7005	09:20:00	11:00:00	2024-10-22	31	236
7006	09:20:00	11:00:00	2024-10-29	31	236
7007	09:20:00	11:00:00	2024-11-05	31	236
7008	09:20:00	11:00:00	2024-11-12	31	236
7009	09:20:00	11:00:00	2024-11-19	31	236
7010	09:20:00	11:00:00	2024-11-26	31	236
7011	09:20:00	11:00:00	2024-12-03	31	236
7012	09:20:00	11:00:00	2024-12-10	31	236
7013	09:20:00	11:00:00	2024-08-06	32	237
7014	09:20:00	11:00:00	2024-08-13	32	237
7015	09:20:00	11:00:00	2024-08-20	32	237
7016	09:20:00	11:00:00	2024-08-27	32	237
7017	09:20:00	11:00:00	2024-09-03	32	237
7018	09:20:00	11:00:00	2024-09-10	32	237
7019	09:20:00	11:00:00	2024-09-17	32	237
7020	09:20:00	11:00:00	2024-09-24	32	237
7021	09:20:00	11:00:00	2024-10-01	32	237
7022	09:20:00	11:00:00	2024-10-08	32	237
7023	09:20:00	11:00:00	2024-10-15	32	237
7024	09:20:00	11:00:00	2024-10-22	32	237
7025	09:20:00	11:00:00	2024-10-29	32	237
7026	09:20:00	11:00:00	2024-11-05	32	237
7027	09:20:00	11:00:00	2024-11-12	32	237
7028	09:20:00	11:00:00	2024-11-19	32	237
7029	09:20:00	11:00:00	2024-11-26	32	237
7030	09:20:00	11:00:00	2024-12-03	32	237
7031	09:20:00	11:00:00	2024-12-10	32	237
7051	07:30:00	09:10:00	2024-08-05	38	241
7052	07:30:00	09:10:00	2024-08-12	38	241
7053	07:30:00	09:10:00	2024-08-19	38	241
7054	07:30:00	09:10:00	2024-08-26	38	241
7055	07:30:00	09:10:00	2024-09-02	38	241
7056	07:30:00	09:10:00	2024-09-09	38	241
7057	07:30:00	09:10:00	2024-09-16	38	241
7058	07:30:00	09:10:00	2024-09-23	38	241
7059	07:30:00	09:10:00	2024-09-30	38	241
7060	07:30:00	09:10:00	2024-10-07	38	241
7061	07:30:00	09:10:00	2024-10-14	38	241
7062	07:30:00	09:10:00	2024-10-21	38	241
7063	07:30:00	09:10:00	2024-10-28	38	241
7064	07:30:00	09:10:00	2024-11-04	38	241
7065	07:30:00	09:10:00	2024-11-11	38	241
7066	07:30:00	09:10:00	2024-11-18	38	241
7067	07:30:00	09:10:00	2024-11-25	38	241
6915	08:20:00	10:00:00	2024-05-06	23	222
6916	08:20:00	10:00:00	2024-05-13	23	222
6917	08:20:00	10:00:00	2024-05-20	23	222
6918	08:20:00	10:00:00	2024-05-27	23	222
6919	08:20:00	10:00:00	2024-06-03	23	222
6920	08:20:00	10:00:00	2024-06-10	23	222
6921	08:20:00	10:00:00	2024-06-17	23	222
6922	08:20:00	10:00:00	2024-06-24	23	222
6923	08:20:00	10:00:00	2024-07-01	23	222
6924	08:20:00	10:00:00	2024-07-08	23	222
6925	08:20:00	10:00:00	2024-07-15	23	222
6926	08:20:00	10:00:00	2024-07-22	23	222
6927	08:20:00	10:00:00	2024-07-29	23	222
6928	08:20:00	10:00:00	2024-08-05	23	222
6929	08:20:00	10:00:00	2024-08-12	23	222
6930	10:20:00	12:00:00	2024-05-08	23	223
6931	10:20:00	12:00:00	2024-05-15	23	223
6932	10:20:00	12:00:00	2024-05-22	23	223
6933	10:20:00	12:00:00	2024-05-29	23	223
6934	10:20:00	12:00:00	2024-06-05	23	223
6935	10:20:00	12:00:00	2024-06-12	23	223
6936	10:20:00	12:00:00	2024-06-19	23	223
6937	10:20:00	12:00:00	2024-06-26	23	223
6938	10:20:00	12:00:00	2024-07-03	23	223
6939	10:20:00	12:00:00	2024-07-10	23	223
6940	10:20:00	12:00:00	2024-07-17	23	223
6941	10:20:00	12:00:00	2024-07-24	23	223
6942	10:20:00	12:00:00	2024-07-31	23	223
6943	10:20:00	12:00:00	2024-08-07	23	223
6944	10:20:00	12:00:00	2024-08-14	23	223
7032	09:20:00	11:00:00	2024-08-06	33	238
7033	09:20:00	11:00:00	2024-08-13	33	238
7034	09:20:00	11:00:00	2024-08-20	33	238
7035	09:20:00	11:00:00	2024-08-27	33	238
7036	09:20:00	11:00:00	2024-09-03	33	238
7037	09:20:00	11:00:00	2024-09-10	33	238
7038	09:20:00	11:00:00	2024-09-17	33	238
7039	09:20:00	11:00:00	2024-09-24	33	238
7040	09:20:00	11:00:00	2024-10-01	33	238
7041	09:20:00	11:00:00	2024-10-08	33	238
7042	09:20:00	11:00:00	2024-10-15	33	238
7043	09:20:00	11:00:00	2024-10-22	33	238
7044	09:20:00	11:00:00	2024-10-29	33	238
7045	09:20:00	11:00:00	2024-11-05	33	238
7046	09:20:00	11:00:00	2024-11-12	33	238
7047	09:20:00	11:00:00	2024-11-19	33	238
7048	09:20:00	11:00:00	2024-11-26	33	238
7049	09:20:00	11:00:00	2024-12-03	33	238
7050	09:20:00	11:00:00	2024-12-10	33	238
7089	07:30:00	09:10:00	2024-08-05	31	251
7090	07:30:00	09:10:00	2024-08-12	31	251
7091	07:30:00	09:10:00	2024-08-19	31	251
7092	07:30:00	09:10:00	2024-08-26	31	251
7093	07:30:00	09:10:00	2024-09-02	31	251
7094	07:30:00	09:10:00	2024-09-09	31	251
7095	07:30:00	09:10:00	2024-09-16	31	251
7096	07:30:00	09:10:00	2024-09-23	31	251
7097	07:30:00	09:10:00	2024-09-30	31	251
7098	07:30:00	09:10:00	2024-10-07	31	251
7099	07:30:00	09:10:00	2024-10-14	31	251
7100	07:30:00	09:10:00	2024-10-21	31	251
7101	07:30:00	09:10:00	2024-10-28	31	251
7102	07:30:00	09:10:00	2024-11-04	31	251
7103	07:30:00	09:10:00	2024-11-11	31	251
7104	07:30:00	09:10:00	2024-11-18	31	251
7105	07:30:00	09:10:00	2024-11-25	31	251
7106	07:30:00	09:10:00	2024-12-02	31	251
7107	07:30:00	09:10:00	2024-12-09	31	251
7108	07:30:00	09:10:00	2024-08-08	31	252
7109	07:30:00	09:10:00	2024-08-15	31	252
7110	07:30:00	09:10:00	2024-08-22	31	252
7111	07:30:00	09:10:00	2024-08-29	31	252
7112	07:30:00	09:10:00	2024-09-05	31	252
7113	07:30:00	09:10:00	2024-09-12	31	252
7114	07:30:00	09:10:00	2024-09-19	31	252
7115	07:30:00	09:10:00	2024-09-26	31	252
7116	07:30:00	09:10:00	2024-10-03	31	252
7117	07:30:00	09:10:00	2024-10-10	31	252
7118	07:30:00	09:10:00	2024-10-17	31	252
7119	07:30:00	09:10:00	2024-10-24	31	252
7120	07:30:00	09:10:00	2024-10-31	31	252
7121	07:30:00	09:10:00	2024-11-07	31	252
7122	07:30:00	09:10:00	2024-11-14	31	252
7123	07:30:00	09:10:00	2024-11-21	31	252
7124	07:30:00	09:10:00	2024-11-28	31	252
7125	07:30:00	09:10:00	2024-12-05	31	252
7126	07:30:00	09:10:00	2024-12-12	31	252
7127	11:10:00	12:50:00	2024-08-06	24	257
7128	11:10:00	12:50:00	2024-08-13	24	257
7129	11:10:00	12:50:00	2024-08-20	24	257
7130	11:10:00	12:50:00	2024-08-27	24	257
7131	11:10:00	12:50:00	2024-09-03	24	257
7132	11:10:00	12:50:00	2024-09-10	24	257
7133	11:10:00	12:50:00	2024-09-17	24	257
7134	11:10:00	12:50:00	2024-09-24	24	257
7135	11:10:00	12:50:00	2024-10-01	24	257
7136	11:10:00	12:50:00	2024-10-08	24	257
7137	11:10:00	12:50:00	2024-10-15	24	257
7138	11:10:00	12:50:00	2024-10-22	24	257
7139	11:10:00	12:50:00	2024-10-29	24	257
7140	11:10:00	12:50:00	2024-11-05	24	257
7141	11:10:00	12:50:00	2024-11-12	24	257
7142	11:10:00	12:50:00	2024-11-19	24	257
7143	11:10:00	12:50:00	2024-11-26	24	257
7144	11:10:00	12:50:00	2024-12-03	24	257
7145	11:10:00	12:50:00	2024-12-10	24	257
7146	11:10:00	12:50:00	2024-08-09	30	262
7147	11:10:00	12:50:00	2024-08-16	30	262
7148	11:10:00	12:50:00	2024-08-23	30	262
7149	11:10:00	12:50:00	2024-08-30	30	262
7150	11:10:00	12:50:00	2024-09-06	30	262
7151	11:10:00	12:50:00	2024-09-13	30	262
7152	11:10:00	12:50:00	2024-09-20	30	262
7153	11:10:00	12:50:00	2024-09-27	30	262
7154	11:10:00	12:50:00	2024-10-04	30	262
7155	11:10:00	12:50:00	2024-10-11	30	262
7156	11:10:00	12:50:00	2024-10-18	30	262
7157	11:10:00	12:50:00	2024-10-25	30	262
7158	11:10:00	12:50:00	2024-11-01	30	262
7159	11:10:00	12:50:00	2024-11-08	30	262
7068	07:30:00	09:10:00	2024-12-02	38	241
7069	07:30:00	09:10:00	2024-12-09	38	241
7070	07:30:00	09:10:00	2024-08-08	38	242
7071	07:30:00	09:10:00	2024-08-15	38	242
7072	07:30:00	09:10:00	2024-08-22	38	242
7073	07:30:00	09:10:00	2024-08-29	38	242
7074	07:30:00	09:10:00	2024-09-05	38	242
7075	07:30:00	09:10:00	2024-09-12	38	242
7076	07:30:00	09:10:00	2024-09-19	38	242
7077	07:30:00	09:10:00	2024-09-26	38	242
7078	07:30:00	09:10:00	2024-10-03	38	242
7079	07:30:00	09:10:00	2024-10-10	38	242
7080	07:30:00	09:10:00	2024-10-17	38	242
7081	07:30:00	09:10:00	2024-10-24	38	242
7082	07:30:00	09:10:00	2024-10-31	38	242
7083	07:30:00	09:10:00	2024-11-07	38	242
7084	07:30:00	09:10:00	2024-11-14	38	242
7085	07:30:00	09:10:00	2024-11-21	38	242
7086	07:30:00	09:10:00	2024-11-28	38	242
7087	07:30:00	09:10:00	2024-12-05	38	242
7088	07:30:00	09:10:00	2024-12-12	38	242
7399	09:20:00	11:00:00	2024-08-07	80	495
7400	09:20:00	11:00:00	2024-08-14	80	495
7401	09:20:00	11:00:00	2024-08-21	80	495
7402	09:20:00	11:00:00	2024-08-28	80	495
7403	09:20:00	11:00:00	2024-09-04	80	495
7404	09:20:00	11:00:00	2024-09-11	80	495
7405	09:20:00	11:00:00	2024-09-18	80	495
7406	09:20:00	11:00:00	2024-09-25	80	495
7407	09:20:00	11:00:00	2024-10-02	80	495
7408	09:20:00	11:00:00	2024-10-09	80	495
7409	09:20:00	11:00:00	2024-10-16	80	495
7410	09:20:00	11:00:00	2024-10-23	80	495
7411	09:20:00	11:00:00	2024-10-30	80	495
7412	09:20:00	11:00:00	2024-11-06	80	495
7413	09:20:00	11:00:00	2024-11-13	80	495
7414	09:20:00	11:00:00	2024-11-20	80	495
7415	09:20:00	11:00:00	2024-11-27	80	495
7416	09:20:00	11:00:00	2024-12-04	80	495
7417	09:20:00	11:00:00	2024-12-11	80	495
7160	11:10:00	12:50:00	2024-11-15	30	262
7161	11:10:00	12:50:00	2024-11-22	30	262
7162	11:10:00	12:50:00	2024-11-29	30	262
7163	11:10:00	12:50:00	2024-12-06	30	262
7164	14:00:00	15:40:00	2024-09-04	23	474
7165	14:00:00	15:40:00	2024-09-11	23	474
7166	14:00:00	15:40:00	2024-09-18	23	474
7167	14:00:00	15:40:00	2024-09-25	23	474
7168	14:00:00	15:40:00	2024-10-02	23	474
7169	14:00:00	15:40:00	2024-10-09	23	474
7170	14:00:00	15:40:00	2024-10-16	23	474
7171	14:00:00	15:40:00	2024-10-23	23	474
7172	14:00:00	15:40:00	2024-10-30	23	474
7173	14:00:00	15:40:00	2024-11-06	23	474
7174	14:00:00	15:40:00	2024-11-13	23	474
7175	14:00:00	15:40:00	2024-11-20	23	474
7176	14:00:00	15:40:00	2024-11-27	23	474
7177	14:00:00	15:40:00	2024-12-04	23	474
7178	14:00:00	15:40:00	2024-12-11	23	474
7179	10:20:00	12:00:00	2024-09-06	23	475
7180	10:20:00	12:00:00	2024-09-13	23	475
7181	10:20:00	12:00:00	2024-09-20	23	475
7182	10:20:00	12:00:00	2024-09-27	23	475
7183	10:20:00	12:00:00	2024-10-04	23	475
7184	10:20:00	12:00:00	2024-10-11	23	475
7185	10:20:00	12:00:00	2024-10-18	23	475
7186	10:20:00	12:00:00	2024-10-25	23	475
7187	10:20:00	12:00:00	2024-11-01	23	475
7188	10:20:00	12:00:00	2024-11-08	23	475
7189	10:20:00	12:00:00	2024-11-15	23	475
7190	10:20:00	12:00:00	2024-11-22	23	475
7191	10:20:00	12:00:00	2024-11-29	23	475
7192	10:20:00	12:00:00	2024-12-06	23	475
7193	10:20:00	12:00:00	2024-12-13	23	475
7194	13:10:00	16:40:00	2024-08-07	76	476
7195	13:10:00	16:40:00	2024-08-14	76	476
7196	13:10:00	16:40:00	2024-08-21	76	476
7197	13:10:00	16:40:00	2024-08-28	76	476
7198	13:10:00	16:40:00	2024-09-04	76	476
7199	13:10:00	16:40:00	2024-09-11	76	476
7200	13:10:00	16:40:00	2024-09-18	76	476
7201	13:10:00	16:40:00	2024-09-25	76	476
7202	13:10:00	16:40:00	2024-10-02	76	476
7203	13:10:00	16:40:00	2024-10-09	76	476
7204	13:10:00	16:40:00	2024-10-16	76	476
7205	13:10:00	16:40:00	2024-10-23	76	476
7206	13:10:00	16:40:00	2024-10-30	76	476
7207	13:10:00	16:40:00	2024-11-06	76	476
7208	13:10:00	16:40:00	2024-11-13	76	476
7209	13:10:00	16:40:00	2024-11-20	76	476
7210	13:10:00	16:40:00	2024-11-27	76	476
7211	13:10:00	16:40:00	2024-12-04	76	476
7212	13:10:00	16:40:00	2024-12-11	76	476
7213	13:10:00	16:40:00	2024-08-07	76	477
7214	13:10:00	16:40:00	2024-08-14	76	477
7215	13:10:00	16:40:00	2024-08-21	76	477
7216	13:10:00	16:40:00	2024-08-28	76	477
7217	13:10:00	16:40:00	2024-09-04	76	477
7218	13:10:00	16:40:00	2024-09-11	76	477
7219	13:10:00	16:40:00	2024-09-18	76	477
7220	13:10:00	16:40:00	2024-09-25	76	477
7221	13:10:00	16:40:00	2024-10-02	76	477
7222	13:10:00	16:40:00	2024-10-09	76	477
7223	13:10:00	16:40:00	2024-10-16	76	477
7224	13:10:00	16:40:00	2024-10-23	76	477
7225	13:10:00	16:40:00	2024-10-30	76	477
7226	13:10:00	16:40:00	2024-11-06	76	477
7227	13:10:00	16:40:00	2024-11-13	76	477
7228	13:10:00	16:40:00	2024-11-20	76	477
7229	13:10:00	16:40:00	2024-11-27	76	477
7230	13:10:00	16:40:00	2024-12-04	76	477
7231	13:10:00	16:40:00	2024-12-11	76	477
7232	13:10:00	14:50:00	2024-08-05	76	478
7233	13:10:00	14:50:00	2024-08-12	76	478
7234	13:10:00	14:50:00	2024-08-19	76	478
7235	13:10:00	14:50:00	2024-08-26	76	478
7236	13:10:00	14:50:00	2024-09-02	76	478
7237	13:10:00	14:50:00	2024-09-09	76	478
7238	13:10:00	14:50:00	2024-09-16	76	478
7239	13:10:00	14:50:00	2024-09-23	76	478
7240	13:10:00	14:50:00	2024-09-30	76	478
7241	13:10:00	14:50:00	2024-10-07	76	478
7242	13:10:00	14:50:00	2024-10-14	76	478
7243	13:10:00	14:50:00	2024-10-21	76	478
7244	13:10:00	14:50:00	2024-10-28	76	478
7245	13:10:00	14:50:00	2024-11-04	76	478
7246	13:10:00	14:50:00	2024-11-11	76	478
7247	13:10:00	14:50:00	2024-11-18	76	478
7248	13:10:00	14:50:00	2024-11-25	76	478
7249	13:10:00	14:50:00	2024-12-02	76	478
7250	13:10:00	14:50:00	2024-12-09	76	478
7251	13:10:00	16:40:00	2024-08-06	77	479
7252	13:10:00	16:40:00	2024-08-13	77	479
7253	13:10:00	16:40:00	2024-08-20	77	479
7254	13:10:00	16:40:00	2024-08-27	77	479
7255	13:10:00	16:40:00	2024-09-03	77	479
7256	13:10:00	16:40:00	2024-09-10	77	479
7257	13:10:00	16:40:00	2024-09-17	77	479
7258	13:10:00	16:40:00	2024-09-24	77	479
7259	13:10:00	16:40:00	2024-10-01	77	479
7260	13:10:00	16:40:00	2024-10-08	77	479
7261	13:10:00	16:40:00	2024-10-15	77	479
7262	13:10:00	16:40:00	2024-10-22	77	479
7263	13:10:00	16:40:00	2024-10-29	77	479
7264	13:10:00	16:40:00	2024-11-05	77	479
7265	13:10:00	16:40:00	2024-11-12	77	479
7266	13:10:00	16:40:00	2024-11-19	77	479
7267	13:10:00	16:40:00	2024-11-26	77	479
7268	13:10:00	16:40:00	2024-12-03	77	479
7269	13:10:00	16:40:00	2024-12-10	77	479
7270	13:10:00	16:40:00	2024-08-06	77	480
7271	13:10:00	16:40:00	2024-08-13	77	480
7272	13:10:00	16:40:00	2024-08-20	77	480
7273	13:10:00	16:40:00	2024-08-27	77	480
7274	13:10:00	16:40:00	2024-09-03	77	480
7275	13:10:00	16:40:00	2024-09-10	77	480
7276	13:10:00	16:40:00	2024-09-17	77	480
7277	13:10:00	16:40:00	2024-09-24	77	480
7278	13:10:00	16:40:00	2024-10-01	77	480
7279	13:10:00	16:40:00	2024-10-08	77	480
7280	13:10:00	16:40:00	2024-10-15	77	480
7281	13:10:00	16:40:00	2024-10-22	77	480
7282	13:10:00	16:40:00	2024-10-29	77	480
7283	13:10:00	16:40:00	2024-11-05	77	480
7284	13:10:00	16:40:00	2024-11-12	77	480
7285	13:10:00	16:40:00	2024-11-19	77	480
7286	13:10:00	16:40:00	2024-11-26	77	480
7287	13:10:00	16:40:00	2024-12-03	77	480
7288	13:10:00	16:40:00	2024-12-10	77	480
7289	13:10:00	16:40:00	2024-08-09	77	481
7290	13:10:00	16:40:00	2024-08-16	77	481
7291	13:10:00	16:40:00	2024-08-23	77	481
7292	13:10:00	16:40:00	2024-08-30	77	481
7293	13:10:00	16:40:00	2024-09-06	77	481
7294	13:10:00	16:40:00	2024-09-13	77	481
7295	13:10:00	16:40:00	2024-09-20	77	481
7296	13:10:00	16:40:00	2024-09-27	77	481
7297	13:10:00	16:40:00	2024-10-04	77	481
7298	13:10:00	16:40:00	2024-10-11	77	481
7299	13:10:00	16:40:00	2024-10-18	77	481
7300	13:10:00	16:40:00	2024-10-25	77	481
7301	13:10:00	16:40:00	2024-11-01	77	481
7302	13:10:00	16:40:00	2024-11-08	77	481
7303	13:10:00	16:40:00	2024-11-15	77	481
7304	13:10:00	16:40:00	2024-11-22	77	481
7305	13:10:00	16:40:00	2024-11-29	77	481
7306	13:10:00	16:40:00	2024-12-06	77	481
7307	13:10:00	16:40:00	2024-08-09	77	482
7308	13:10:00	16:40:00	2024-08-16	77	482
7309	13:10:00	16:40:00	2024-08-23	77	482
7310	13:10:00	16:40:00	2024-08-30	77	482
7311	13:10:00	16:40:00	2024-09-06	77	482
7312	13:10:00	16:40:00	2024-09-13	77	482
7313	13:10:00	16:40:00	2024-09-20	77	482
7314	13:10:00	16:40:00	2024-09-27	77	482
7315	13:10:00	16:40:00	2024-10-04	77	482
7316	13:10:00	16:40:00	2024-10-11	77	482
7317	13:10:00	16:40:00	2024-10-18	77	482
7318	13:10:00	16:40:00	2024-10-25	77	482
7319	13:10:00	16:40:00	2024-11-01	77	482
7320	13:10:00	16:40:00	2024-11-08	77	482
7321	13:10:00	16:40:00	2024-11-15	77	482
7322	13:10:00	16:40:00	2024-11-22	77	482
7323	13:10:00	16:40:00	2024-11-29	77	482
7324	13:10:00	16:40:00	2024-12-06	77	482
7325	07:30:00	11:00:00	2024-08-08	78	483
7326	07:30:00	11:00:00	2024-08-15	78	483
7327	07:30:00	11:00:00	2024-08-22	78	483
7328	07:30:00	11:00:00	2024-08-29	78	483
7329	07:30:00	11:00:00	2024-09-05	78	483
7330	07:30:00	11:00:00	2024-09-12	78	483
7331	07:30:00	11:00:00	2024-09-19	78	483
7332	07:30:00	11:00:00	2024-09-26	78	483
7333	07:30:00	11:00:00	2024-10-03	78	483
7334	07:30:00	11:00:00	2024-10-10	78	483
7335	07:30:00	11:00:00	2024-10-17	78	483
7336	07:30:00	11:00:00	2024-10-24	78	483
7337	07:30:00	11:00:00	2024-10-31	78	483
7338	07:30:00	11:00:00	2024-11-07	78	483
7339	07:30:00	11:00:00	2024-11-14	78	483
7340	07:30:00	11:00:00	2024-11-21	78	483
7341	07:30:00	11:00:00	2024-11-28	78	483
7342	07:30:00	11:00:00	2024-12-05	78	483
7343	07:30:00	11:00:00	2024-12-12	78	483
7344	07:30:00	11:00:00	2024-08-08	78	484
7345	07:30:00	11:00:00	2024-08-15	78	484
7346	07:30:00	11:00:00	2024-08-22	78	484
7347	07:30:00	11:00:00	2024-08-29	78	484
7348	07:30:00	11:00:00	2024-09-05	78	484
7349	07:30:00	11:00:00	2024-09-12	78	484
7350	07:30:00	11:00:00	2024-09-19	78	484
7351	07:30:00	11:00:00	2024-09-26	78	484
7352	07:30:00	11:00:00	2024-10-03	78	484
7353	07:30:00	11:00:00	2024-10-10	78	484
7354	07:30:00	11:00:00	2024-10-17	78	484
7355	07:30:00	11:00:00	2024-10-24	78	484
7356	07:30:00	11:00:00	2024-10-31	78	484
7357	07:30:00	11:00:00	2024-11-07	78	484
7358	07:30:00	11:00:00	2024-11-14	78	484
7359	07:30:00	11:00:00	2024-11-21	78	484
7360	07:30:00	11:00:00	2024-11-28	78	484
7361	07:30:00	11:00:00	2024-12-05	78	484
7362	07:30:00	11:00:00	2024-12-12	78	484
7363	13:10:00	16:40:00	2024-08-09	78	485
7364	13:10:00	16:40:00	2024-08-16	78	485
7365	13:10:00	16:40:00	2024-08-23	78	485
7366	13:10:00	16:40:00	2024-08-30	78	485
7367	13:10:00	16:40:00	2024-09-06	78	485
7368	13:10:00	16:40:00	2024-09-13	78	485
7369	13:10:00	16:40:00	2024-09-20	78	485
7370	13:10:00	16:40:00	2024-09-27	78	485
7371	13:10:00	16:40:00	2024-10-04	78	485
7372	13:10:00	16:40:00	2024-10-11	78	485
7373	13:10:00	16:40:00	2024-10-18	78	485
7374	13:10:00	16:40:00	2024-10-25	78	485
7375	13:10:00	16:40:00	2024-11-01	78	485
7376	13:10:00	16:40:00	2024-11-08	78	485
7377	13:10:00	16:40:00	2024-11-15	78	485
7378	13:10:00	16:40:00	2024-11-22	78	485
7379	13:10:00	16:40:00	2024-11-29	78	485
7380	13:10:00	16:40:00	2024-12-06	78	485
7381	13:10:00	16:40:00	2024-08-09	78	486
7382	13:10:00	16:40:00	2024-08-16	78	486
7383	13:10:00	16:40:00	2024-08-23	78	486
7384	13:10:00	16:40:00	2024-08-30	78	486
7385	13:10:00	16:40:00	2024-09-06	78	486
7386	13:10:00	16:40:00	2024-09-13	78	486
7387	13:10:00	16:40:00	2024-09-20	78	486
7388	13:10:00	16:40:00	2024-09-27	78	486
7389	13:10:00	16:40:00	2024-10-04	78	486
7390	13:10:00	16:40:00	2024-10-11	78	486
7391	13:10:00	16:40:00	2024-10-18	78	486
7392	13:10:00	16:40:00	2024-10-25	78	486
7393	13:10:00	16:40:00	2024-11-01	78	486
7394	13:10:00	16:40:00	2024-11-08	78	486
7395	13:10:00	16:40:00	2024-11-15	78	486
7396	13:10:00	16:40:00	2024-11-22	78	486
7397	13:10:00	16:40:00	2024-11-29	78	486
7398	13:10:00	16:40:00	2024-12-06	78	486
7494	14:00:00	17:20:00	2024-08-05	79	500
7418	09:20:00	11:00:00	2024-08-07	81	496
7419	09:20:00	11:00:00	2024-08-14	81	496
7420	09:20:00	11:00:00	2024-08-21	81	496
7421	09:20:00	11:00:00	2024-08-28	81	496
7422	09:20:00	11:00:00	2024-09-04	81	496
7423	09:20:00	11:00:00	2024-09-11	81	496
7424	09:20:00	11:00:00	2024-09-18	81	496
7425	09:20:00	11:00:00	2024-09-25	81	496
7426	09:20:00	11:00:00	2024-10-02	81	496
7427	09:20:00	11:00:00	2024-10-09	81	496
7428	09:20:00	11:00:00	2024-10-16	81	496
7429	09:20:00	11:00:00	2024-10-23	81	496
7430	09:20:00	11:00:00	2024-10-30	81	496
7431	09:20:00	11:00:00	2024-11-06	81	496
7432	09:20:00	11:00:00	2024-11-13	81	496
7433	09:20:00	11:00:00	2024-11-20	81	496
7434	09:20:00	11:00:00	2024-11-27	81	496
7435	09:20:00	11:00:00	2024-12-04	81	496
7436	09:20:00	11:00:00	2024-12-11	81	496
7437	09:20:00	11:00:00	2024-08-05	80	497
7438	09:20:00	11:00:00	2024-08-12	80	497
7439	09:20:00	11:00:00	2024-08-19	80	497
7440	09:20:00	11:00:00	2024-08-26	80	497
7441	09:20:00	11:00:00	2024-09-02	80	497
7442	09:20:00	11:00:00	2024-09-09	80	497
7443	09:20:00	11:00:00	2024-09-16	80	497
7444	09:20:00	11:00:00	2024-09-23	80	497
7445	09:20:00	11:00:00	2024-09-30	80	497
7446	09:20:00	11:00:00	2024-10-07	80	497
7447	09:20:00	11:00:00	2024-10-14	80	497
7448	09:20:00	11:00:00	2024-10-21	80	497
7449	09:20:00	11:00:00	2024-10-28	80	497
7450	09:20:00	11:00:00	2024-11-04	80	497
7451	09:20:00	11:00:00	2024-11-11	80	497
7452	09:20:00	11:00:00	2024-11-18	80	497
7453	09:20:00	11:00:00	2024-11-25	80	497
7454	09:20:00	11:00:00	2024-12-02	80	497
7455	09:20:00	11:00:00	2024-12-09	80	497
7456	09:20:00	11:00:00	2024-08-05	76	498
7457	09:20:00	11:00:00	2024-08-12	76	498
7458	09:20:00	11:00:00	2024-08-19	76	498
7459	09:20:00	11:00:00	2024-08-26	76	498
7460	09:20:00	11:00:00	2024-09-02	76	498
7461	09:20:00	11:00:00	2024-09-09	76	498
7462	09:20:00	11:00:00	2024-09-16	76	498
7463	09:20:00	11:00:00	2024-09-23	76	498
7464	09:20:00	11:00:00	2024-09-30	76	498
7465	09:20:00	11:00:00	2024-10-07	76	498
7466	09:20:00	11:00:00	2024-10-14	76	498
7467	09:20:00	11:00:00	2024-10-21	76	498
7468	09:20:00	11:00:00	2024-10-28	76	498
7469	09:20:00	11:00:00	2024-11-04	76	498
7470	09:20:00	11:00:00	2024-11-11	76	498
7471	09:20:00	11:00:00	2024-11-18	76	498
7472	09:20:00	11:00:00	2024-11-25	76	498
7473	09:20:00	11:00:00	2024-12-02	76	498
7474	09:20:00	11:00:00	2024-12-09	76	498
7475	14:00:00	17:20:00	2024-08-05	79	499
7476	14:00:00	17:20:00	2024-08-12	79	499
7477	14:00:00	17:20:00	2024-08-19	79	499
7478	14:00:00	17:20:00	2024-08-26	79	499
7479	14:00:00	17:20:00	2024-09-02	79	499
7480	14:00:00	17:20:00	2024-09-09	79	499
7481	14:00:00	17:20:00	2024-09-16	79	499
7482	14:00:00	17:20:00	2024-09-23	79	499
7483	14:00:00	17:20:00	2024-09-30	79	499
7484	14:00:00	17:20:00	2024-10-07	79	499
7485	14:00:00	17:20:00	2024-10-14	79	499
7486	14:00:00	17:20:00	2024-10-21	79	499
7487	14:00:00	17:20:00	2024-10-28	79	499
7488	14:00:00	17:20:00	2024-11-04	79	499
7489	14:00:00	17:20:00	2024-11-11	79	499
7490	14:00:00	17:20:00	2024-11-18	79	499
7491	14:00:00	17:20:00	2024-11-25	79	499
7492	14:00:00	17:20:00	2024-12-02	79	499
7493	14:00:00	17:20:00	2024-12-09	79	499
7495	14:00:00	17:20:00	2024-08-12	79	500
7496	14:00:00	17:20:00	2024-08-19	79	500
7497	14:00:00	17:20:00	2024-08-26	79	500
7498	14:00:00	17:20:00	2024-09-02	79	500
7499	14:00:00	17:20:00	2024-09-09	79	500
7500	14:00:00	17:20:00	2024-09-16	79	500
7501	14:00:00	17:20:00	2024-09-23	79	500
7502	14:00:00	17:20:00	2024-09-30	79	500
7503	14:00:00	17:20:00	2024-10-07	79	500
7504	14:00:00	17:20:00	2024-10-14	79	500
7505	14:00:00	17:20:00	2024-10-21	79	500
7506	14:00:00	17:20:00	2024-10-28	79	500
7507	14:00:00	17:20:00	2024-11-04	79	500
7508	14:00:00	17:20:00	2024-11-11	79	500
7509	14:00:00	17:20:00	2024-11-18	79	500
7510	14:00:00	17:20:00	2024-11-25	79	500
7511	14:00:00	17:20:00	2024-12-02	79	500
7512	14:00:00	17:20:00	2024-12-09	79	500
7513	07:30:00	11:00:00	2024-08-06	80	501
7514	07:30:00	11:00:00	2024-08-13	80	501
7515	07:30:00	11:00:00	2024-08-20	80	501
7516	07:30:00	11:00:00	2024-08-27	80	501
7517	07:30:00	11:00:00	2024-09-03	80	501
7518	07:30:00	11:00:00	2024-09-10	80	501
7519	07:30:00	11:00:00	2024-09-17	80	501
7520	07:30:00	11:00:00	2024-09-24	80	501
7521	07:30:00	11:00:00	2024-10-01	80	501
7522	07:30:00	11:00:00	2024-10-08	80	501
7523	07:30:00	11:00:00	2024-10-15	80	501
7524	07:30:00	11:00:00	2024-10-22	80	501
7525	07:30:00	11:00:00	2024-10-29	80	501
7526	07:30:00	11:00:00	2024-11-05	80	501
7527	07:30:00	11:00:00	2024-11-12	80	501
7528	07:30:00	11:00:00	2024-11-19	80	501
7529	07:30:00	11:00:00	2024-11-26	80	501
7530	07:30:00	11:00:00	2024-12-03	80	501
7531	07:30:00	11:00:00	2024-12-10	80	501
7532	07:30:00	11:00:00	2024-08-06	80	502
7533	07:30:00	11:00:00	2024-08-13	80	502
7534	07:30:00	11:00:00	2024-08-20	80	502
7535	07:30:00	11:00:00	2024-08-27	80	502
7536	07:30:00	11:00:00	2024-09-03	80	502
7537	07:30:00	11:00:00	2024-09-10	80	502
7538	07:30:00	11:00:00	2024-09-17	80	502
7539	07:30:00	11:00:00	2024-09-24	80	502
7540	07:30:00	11:00:00	2024-10-01	80	502
7541	07:30:00	11:00:00	2024-10-08	80	502
7542	07:30:00	11:00:00	2024-10-15	80	502
7543	07:30:00	11:00:00	2024-10-22	80	502
7544	07:30:00	11:00:00	2024-10-29	80	502
7545	07:30:00	11:00:00	2024-11-05	80	502
7546	07:30:00	11:00:00	2024-11-12	80	502
7547	07:30:00	11:00:00	2024-11-19	80	502
7548	07:30:00	11:00:00	2024-11-26	80	502
7549	07:30:00	11:00:00	2024-12-03	80	502
7550	07:30:00	11:00:00	2024-12-10	80	502
7551	07:30:00	11:00:00	2024-08-07	82	503
7552	07:30:00	11:00:00	2024-08-14	82	503
7553	07:30:00	11:00:00	2024-08-21	82	503
7554	07:30:00	11:00:00	2024-08-28	82	503
7555	07:30:00	11:00:00	2024-09-04	82	503
7556	07:30:00	11:00:00	2024-09-11	82	503
7557	07:30:00	11:00:00	2024-09-18	82	503
7558	07:30:00	11:00:00	2024-09-25	82	503
7559	07:30:00	11:00:00	2024-10-02	82	503
7560	07:30:00	11:00:00	2024-10-09	82	503
7561	07:30:00	11:00:00	2024-10-16	82	503
7562	07:30:00	11:00:00	2024-10-23	82	503
7563	07:30:00	11:00:00	2024-10-30	82	503
7564	07:30:00	11:00:00	2024-11-06	82	503
7565	07:30:00	11:00:00	2024-11-13	82	503
7566	07:30:00	11:00:00	2024-11-20	82	503
7567	07:30:00	11:00:00	2024-11-27	82	503
7568	07:30:00	11:00:00	2024-12-04	82	503
7569	07:30:00	11:00:00	2024-12-11	82	503
7570	07:30:00	11:00:00	2024-08-07	82	504
7571	07:30:00	11:00:00	2024-08-14	82	504
7572	07:30:00	11:00:00	2024-08-21	82	504
7573	07:30:00	11:00:00	2024-08-28	82	504
7574	07:30:00	11:00:00	2024-09-04	82	504
7575	07:30:00	11:00:00	2024-09-11	82	504
7576	07:30:00	11:00:00	2024-09-18	82	504
7577	07:30:00	11:00:00	2024-09-25	82	504
7578	07:30:00	11:00:00	2024-10-02	82	504
7579	07:30:00	11:00:00	2024-10-09	82	504
7580	07:30:00	11:00:00	2024-10-16	82	504
7581	07:30:00	11:00:00	2024-10-23	82	504
7582	07:30:00	11:00:00	2024-10-30	82	504
7583	07:30:00	11:00:00	2024-11-06	82	504
7584	07:30:00	11:00:00	2024-11-13	82	504
7585	07:30:00	11:00:00	2024-11-20	82	504
7586	07:30:00	11:00:00	2024-11-27	82	504
7587	07:30:00	11:00:00	2024-12-04	82	504
7588	07:30:00	11:00:00	2024-12-11	82	504
7589	07:30:00	11:00:00	2024-08-08	79	505
7590	07:30:00	11:00:00	2024-08-15	79	505
7591	07:30:00	11:00:00	2024-08-22	79	505
7592	07:30:00	11:00:00	2024-08-29	79	505
7593	07:30:00	11:00:00	2024-09-05	79	505
7594	07:30:00	11:00:00	2024-09-12	79	505
7595	07:30:00	11:00:00	2024-09-19	79	505
7596	07:30:00	11:00:00	2024-09-26	79	505
7597	07:30:00	11:00:00	2024-10-03	79	505
7598	07:30:00	11:00:00	2024-10-10	79	505
7599	07:30:00	11:00:00	2024-10-17	79	505
7600	07:30:00	11:00:00	2024-10-24	79	505
7601	07:30:00	11:00:00	2024-10-31	79	505
7602	07:30:00	11:00:00	2024-11-07	79	505
7603	07:30:00	11:00:00	2024-11-14	79	505
7604	07:30:00	11:00:00	2024-11-21	79	505
7605	07:30:00	11:00:00	2024-11-28	79	505
7606	07:30:00	11:00:00	2024-12-05	79	505
7607	07:30:00	11:00:00	2024-12-12	79	505
7608	07:30:00	11:00:00	2024-08-08	79	506
7609	07:30:00	11:00:00	2024-08-15	79	506
7610	07:30:00	11:00:00	2024-08-22	79	506
7611	07:30:00	11:00:00	2024-08-29	79	506
7612	07:30:00	11:00:00	2024-09-05	79	506
7613	07:30:00	11:00:00	2024-09-12	79	506
7614	07:30:00	11:00:00	2024-09-19	79	506
7615	07:30:00	11:00:00	2024-09-26	79	506
7616	07:30:00	11:00:00	2024-10-03	79	506
7617	07:30:00	11:00:00	2024-10-10	79	506
7618	07:30:00	11:00:00	2024-10-17	79	506
7619	07:30:00	11:00:00	2024-10-24	79	506
7620	07:30:00	11:00:00	2024-10-31	79	506
7621	07:30:00	11:00:00	2024-11-07	79	506
7622	07:30:00	11:00:00	2024-11-14	79	506
7623	07:30:00	11:00:00	2024-11-21	79	506
7624	07:30:00	11:00:00	2024-11-28	79	506
7625	07:30:00	11:00:00	2024-12-05	79	506
7626	07:30:00	11:00:00	2024-12-12	79	506
7627	07:30:00	11:00:00	2024-08-08	79	507
7628	07:30:00	11:00:00	2024-08-15	79	507
7629	07:30:00	11:00:00	2024-08-22	79	507
7630	07:30:00	11:00:00	2024-08-29	79	507
7631	07:30:00	11:00:00	2024-09-05	79	507
7632	07:30:00	11:00:00	2024-09-12	79	507
7633	07:30:00	11:00:00	2024-09-19	79	507
7634	07:30:00	11:00:00	2024-09-26	79	507
7635	07:30:00	11:00:00	2024-10-03	79	507
7636	07:30:00	11:00:00	2024-10-10	79	507
7637	07:30:00	11:00:00	2024-10-17	79	507
7638	07:30:00	11:00:00	2024-10-24	79	507
7639	07:30:00	11:00:00	2024-10-31	79	507
7640	07:30:00	11:00:00	2024-11-07	79	507
7641	07:30:00	11:00:00	2024-11-14	79	507
7642	07:30:00	11:00:00	2024-11-21	79	507
7643	07:30:00	11:00:00	2024-11-28	79	507
7644	07:30:00	11:00:00	2024-12-05	79	507
7645	07:30:00	11:00:00	2024-12-12	79	507
7646	07:30:00	11:00:00	2024-08-09	80	508
7647	07:30:00	11:00:00	2024-08-16	80	508
7648	07:30:00	11:00:00	2024-08-23	80	508
7649	07:30:00	11:00:00	2024-08-30	80	508
7650	07:30:00	11:00:00	2024-09-06	80	508
7651	07:30:00	11:00:00	2024-09-13	80	508
7652	07:30:00	11:00:00	2024-09-20	80	508
7653	07:30:00	11:00:00	2024-09-27	80	508
7654	07:30:00	11:00:00	2024-10-04	80	508
7655	07:30:00	11:00:00	2024-10-11	80	508
7656	07:30:00	11:00:00	2024-10-18	80	508
7657	07:30:00	11:00:00	2024-10-25	80	508
7658	07:30:00	11:00:00	2024-11-01	80	508
7659	07:30:00	11:00:00	2024-11-08	80	508
7660	07:30:00	11:00:00	2024-11-15	80	508
7661	07:30:00	11:00:00	2024-11-22	80	508
7662	07:30:00	11:00:00	2024-11-29	80	508
7663	07:30:00	11:00:00	2024-12-06	80	508
7664	07:30:00	11:00:00	2024-08-09	80	509
7665	07:30:00	11:00:00	2024-08-16	80	509
7666	07:30:00	11:00:00	2024-08-23	80	509
7667	07:30:00	11:00:00	2024-08-30	80	509
7668	07:30:00	11:00:00	2024-09-06	80	509
7669	07:30:00	11:00:00	2024-09-13	80	509
7670	07:30:00	11:00:00	2024-09-20	80	509
7671	07:30:00	11:00:00	2024-09-27	80	509
7672	07:30:00	11:00:00	2024-10-04	80	509
7673	07:30:00	11:00:00	2024-10-11	80	509
7674	07:30:00	11:00:00	2024-10-18	80	509
7675	07:30:00	11:00:00	2024-10-25	80	509
7676	07:30:00	11:00:00	2024-11-01	80	509
7677	07:30:00	11:00:00	2024-11-08	80	509
7678	07:30:00	11:00:00	2024-11-15	80	509
7679	07:30:00	11:00:00	2024-11-22	80	509
7680	07:30:00	11:00:00	2024-11-29	80	509
7681	07:30:00	11:00:00	2024-12-06	80	509
7682	07:30:00	11:00:00	2024-08-09	80	510
7683	07:30:00	11:00:00	2024-08-16	80	510
7684	07:30:00	11:00:00	2024-08-23	80	510
7685	07:30:00	11:00:00	2024-08-30	80	510
7686	07:30:00	11:00:00	2024-09-06	80	510
7687	07:30:00	11:00:00	2024-09-13	80	510
7688	07:30:00	11:00:00	2024-09-20	80	510
7689	07:30:00	11:00:00	2024-09-27	80	510
7690	07:30:00	11:00:00	2024-10-04	80	510
7691	07:30:00	11:00:00	2024-10-11	80	510
7692	07:30:00	11:00:00	2024-10-18	80	510
7693	07:30:00	11:00:00	2024-10-25	80	510
7694	07:30:00	11:00:00	2024-11-01	80	510
7695	07:30:00	11:00:00	2024-11-08	80	510
7696	07:30:00	11:00:00	2024-11-15	80	510
7697	07:30:00	11:00:00	2024-11-22	80	510
7698	07:30:00	11:00:00	2024-11-29	80	510
7699	07:30:00	11:00:00	2024-12-06	80	510
7700	13:10:00	16:40:00	2024-08-09	79	511
7701	13:10:00	16:40:00	2024-08-16	79	511
7702	13:10:00	16:40:00	2024-08-23	79	511
7703	13:10:00	16:40:00	2024-08-30	79	511
7704	13:10:00	16:40:00	2024-09-06	79	511
7705	13:10:00	16:40:00	2024-09-13	79	511
7706	13:10:00	16:40:00	2024-09-20	79	511
7707	13:10:00	16:40:00	2024-09-27	79	511
7708	13:10:00	16:40:00	2024-10-04	79	511
7709	13:10:00	16:40:00	2024-10-11	79	511
7710	13:10:00	16:40:00	2024-10-18	79	511
7711	13:10:00	16:40:00	2024-10-25	79	511
7712	13:10:00	16:40:00	2024-11-01	79	511
7713	13:10:00	16:40:00	2024-11-08	79	511
7714	13:10:00	16:40:00	2024-11-15	79	511
7715	13:10:00	16:40:00	2024-11-22	79	511
7716	13:10:00	16:40:00	2024-11-29	79	511
7717	13:10:00	16:40:00	2024-12-06	79	511
7718	13:10:00	16:40:00	2024-08-09	79	512
7719	13:10:00	16:40:00	2024-08-16	79	512
7720	13:10:00	16:40:00	2024-08-23	79	512
7721	13:10:00	16:40:00	2024-08-30	79	512
7722	13:10:00	16:40:00	2024-09-06	79	512
7723	13:10:00	16:40:00	2024-09-13	79	512
7724	13:10:00	16:40:00	2024-09-20	79	512
7725	13:10:00	16:40:00	2024-09-27	79	512
7726	13:10:00	16:40:00	2024-10-04	79	512
7727	13:10:00	16:40:00	2024-10-11	79	512
7728	13:10:00	16:40:00	2024-10-18	79	512
7729	13:10:00	16:40:00	2024-10-25	79	512
7730	13:10:00	16:40:00	2024-11-01	79	512
7731	13:10:00	16:40:00	2024-11-08	79	512
7732	13:10:00	16:40:00	2024-11-15	79	512
7733	13:10:00	16:40:00	2024-11-22	79	512
7734	13:10:00	16:40:00	2024-11-29	79	512
7735	13:10:00	16:40:00	2024-12-06	79	512
7736	15:00:00	16:40:00	2024-08-07	81	514
7737	15:00:00	16:40:00	2024-08-14	81	514
7738	15:00:00	16:40:00	2024-08-21	81	514
7739	15:00:00	16:40:00	2024-08-28	81	514
7740	15:00:00	16:40:00	2024-09-04	81	514
7741	15:00:00	16:40:00	2024-09-11	81	514
7742	15:00:00	16:40:00	2024-09-18	81	514
7743	15:00:00	16:40:00	2024-09-25	81	514
7744	15:00:00	16:40:00	2024-10-02	81	514
7745	15:00:00	16:40:00	2024-10-09	81	514
7746	15:00:00	16:40:00	2024-10-16	81	514
7747	15:00:00	16:40:00	2024-10-23	81	514
7748	15:00:00	16:40:00	2024-10-30	81	514
7749	15:00:00	16:40:00	2024-11-06	81	514
7750	15:00:00	16:40:00	2024-11-13	81	514
7751	15:00:00	16:40:00	2024-11-20	81	514
7752	15:00:00	16:40:00	2024-11-27	81	514
7753	15:00:00	16:40:00	2024-12-04	81	514
7754	15:00:00	16:40:00	2024-12-11	81	514
7755	15:00:00	16:40:00	2024-08-08	81	515
7756	15:00:00	16:40:00	2024-08-15	81	515
7757	15:00:00	16:40:00	2024-08-22	81	515
7758	15:00:00	16:40:00	2024-08-29	81	515
7759	15:00:00	16:40:00	2024-09-05	81	515
7760	15:00:00	16:40:00	2024-09-12	81	515
7761	15:00:00	16:40:00	2024-09-19	81	515
7762	15:00:00	16:40:00	2024-09-26	81	515
7763	15:00:00	16:40:00	2024-10-03	81	515
7764	15:00:00	16:40:00	2024-10-10	81	515
7765	15:00:00	16:40:00	2024-10-17	81	515
7766	15:00:00	16:40:00	2024-10-24	81	515
7767	15:00:00	16:40:00	2024-10-31	81	515
7768	15:00:00	16:40:00	2024-11-07	81	515
7769	15:00:00	16:40:00	2024-11-14	81	515
7770	15:00:00	16:40:00	2024-11-21	81	515
7771	15:00:00	16:40:00	2024-11-28	81	515
7772	15:00:00	16:40:00	2024-12-05	81	515
7773	15:00:00	16:40:00	2024-12-12	81	515
7774	15:00:00	16:40:00	2024-08-09	81	516
7775	15:00:00	16:40:00	2024-08-16	81	516
7776	15:00:00	16:40:00	2024-08-23	81	516
7777	15:00:00	16:40:00	2024-08-30	81	516
7778	15:00:00	16:40:00	2024-09-06	81	516
7779	15:00:00	16:40:00	2024-09-13	81	516
7780	15:00:00	16:40:00	2024-09-20	81	516
7781	15:00:00	16:40:00	2024-09-27	81	516
7782	15:00:00	16:40:00	2024-10-04	81	516
7783	15:00:00	16:40:00	2024-10-11	81	516
7784	15:00:00	16:40:00	2024-10-18	81	516
7785	15:00:00	16:40:00	2024-10-25	81	516
7786	15:00:00	16:40:00	2024-11-01	81	516
7787	15:00:00	16:40:00	2024-11-08	81	516
7788	15:00:00	16:40:00	2024-11-15	81	516
7789	15:00:00	16:40:00	2024-11-22	81	516
7790	15:00:00	16:40:00	2024-11-29	81	516
7791	15:00:00	16:40:00	2024-12-06	81	516
7792	07:30:00	09:10:00	2024-08-05	76	517
7793	07:30:00	09:10:00	2024-08-12	76	517
7794	07:30:00	09:10:00	2024-08-19	76	517
7795	07:30:00	09:10:00	2024-08-26	76	517
7796	07:30:00	09:10:00	2024-09-02	76	517
7797	07:30:00	09:10:00	2024-09-09	76	517
7798	07:30:00	09:10:00	2024-09-16	76	517
7799	07:30:00	09:10:00	2024-09-23	76	517
7800	07:30:00	09:10:00	2024-09-30	76	517
7801	07:30:00	09:10:00	2024-10-07	76	517
7802	07:30:00	09:10:00	2024-10-14	76	517
7803	07:30:00	09:10:00	2024-10-21	76	517
7804	07:30:00	09:10:00	2024-10-28	76	517
7805	07:30:00	09:10:00	2024-11-04	76	517
7806	07:30:00	09:10:00	2024-11-11	76	517
7807	07:30:00	09:10:00	2024-11-18	76	517
7808	07:30:00	09:10:00	2024-11-25	76	517
7809	07:30:00	09:10:00	2024-12-02	76	517
7810	07:30:00	09:10:00	2024-12-09	76	517
7811	07:30:00	09:10:00	2024-08-07	76	518
7812	07:30:00	09:10:00	2024-08-14	76	518
7813	07:30:00	09:10:00	2024-08-21	76	518
7814	07:30:00	09:10:00	2024-08-28	76	518
7815	07:30:00	09:10:00	2024-09-04	76	518
7816	07:30:00	09:10:00	2024-09-11	76	518
7817	07:30:00	09:10:00	2024-09-18	76	518
7818	07:30:00	09:10:00	2024-09-25	76	518
7819	07:30:00	09:10:00	2024-10-02	76	518
7820	07:30:00	09:10:00	2024-10-09	76	518
7821	07:30:00	09:10:00	2024-10-16	76	518
7822	07:30:00	09:10:00	2024-10-23	76	518
7823	07:30:00	09:10:00	2024-10-30	76	518
7824	07:30:00	09:10:00	2024-11-06	76	518
7825	07:30:00	09:10:00	2024-11-13	76	518
7826	07:30:00	09:10:00	2024-11-20	76	518
7827	07:30:00	09:10:00	2024-11-27	76	518
7828	07:30:00	09:10:00	2024-12-04	76	518
7829	07:30:00	09:10:00	2024-12-11	76	518
7867	09:20:00	11:00:00	2024-08-07	84	521
7868	09:20:00	11:00:00	2024-08-14	84	521
7869	09:20:00	11:00:00	2024-08-21	84	521
7870	09:20:00	11:00:00	2024-08-28	84	521
7871	09:20:00	11:00:00	2024-09-04	84	521
7872	09:20:00	11:00:00	2024-09-11	84	521
7873	09:20:00	11:00:00	2024-09-18	84	521
7874	09:20:00	11:00:00	2024-09-25	84	521
7875	09:20:00	11:00:00	2024-10-02	84	521
7876	09:20:00	11:00:00	2024-10-09	84	521
7877	09:20:00	11:00:00	2024-10-16	84	521
7878	09:20:00	11:00:00	2024-10-23	84	521
7879	09:20:00	11:00:00	2024-10-30	84	521
7880	09:20:00	11:00:00	2024-11-06	84	521
7881	09:20:00	11:00:00	2024-11-13	84	521
7882	09:20:00	11:00:00	2024-11-20	84	521
7883	09:20:00	11:00:00	2024-11-27	84	521
7884	09:20:00	11:00:00	2024-12-04	84	521
7885	09:20:00	11:00:00	2024-12-11	84	521
7886	09:20:00	11:00:00	2024-08-09	84	522
7887	09:20:00	11:00:00	2024-08-16	84	522
7888	09:20:00	11:00:00	2024-08-23	84	522
7889	09:20:00	11:00:00	2024-08-30	84	522
7890	09:20:00	11:00:00	2024-09-06	84	522
7891	09:20:00	11:00:00	2024-09-13	84	522
7830	09:20:00	11:00:00	2024-08-06	81	519
7831	09:20:00	11:00:00	2024-08-13	81	519
7832	09:20:00	11:00:00	2024-08-20	81	519
7833	09:20:00	11:00:00	2024-08-27	81	519
7834	09:20:00	11:00:00	2024-09-03	81	519
7835	09:20:00	11:00:00	2024-09-10	81	519
7836	09:20:00	11:00:00	2024-09-17	81	519
7837	09:20:00	11:00:00	2024-09-24	81	519
7838	09:20:00	11:00:00	2024-10-01	81	519
7839	09:20:00	11:00:00	2024-10-08	81	519
7840	09:20:00	11:00:00	2024-10-15	81	519
7841	09:20:00	11:00:00	2024-10-22	81	519
7842	09:20:00	11:00:00	2024-10-29	81	519
7843	09:20:00	11:00:00	2024-11-05	81	519
7844	09:20:00	11:00:00	2024-11-12	81	519
7845	09:20:00	11:00:00	2024-11-19	81	519
7846	09:20:00	11:00:00	2024-11-26	81	519
7847	09:20:00	11:00:00	2024-12-03	81	519
7848	09:20:00	11:00:00	2024-12-10	81	519
7849	07:30:00	09:10:00	2024-08-09	81	520
7850	07:30:00	09:10:00	2024-08-16	81	520
7851	07:30:00	09:10:00	2024-08-23	81	520
7852	07:30:00	09:10:00	2024-08-30	81	520
7853	07:30:00	09:10:00	2024-09-06	81	520
7854	07:30:00	09:10:00	2024-09-13	81	520
7855	07:30:00	09:10:00	2024-09-20	81	520
7856	07:30:00	09:10:00	2024-09-27	81	520
7857	07:30:00	09:10:00	2024-10-04	81	520
7858	07:30:00	09:10:00	2024-10-11	81	520
7859	07:30:00	09:10:00	2024-10-18	81	520
7860	07:30:00	09:10:00	2024-10-25	81	520
7861	07:30:00	09:10:00	2024-11-01	81	520
7862	07:30:00	09:10:00	2024-11-08	81	520
7863	07:30:00	09:10:00	2024-11-15	81	520
7864	07:30:00	09:10:00	2024-11-22	81	520
7865	07:30:00	09:10:00	2024-11-29	81	520
7866	07:30:00	09:10:00	2024-12-06	81	520
7904	09:20:00	11:00:00	2024-08-07	83	523
7905	09:20:00	11:00:00	2024-08-14	83	523
7906	09:20:00	11:00:00	2024-08-21	83	523
7907	09:20:00	11:00:00	2024-08-28	83	523
7908	09:20:00	11:00:00	2024-09-04	83	523
7909	09:20:00	11:00:00	2024-09-11	83	523
7910	09:20:00	11:00:00	2024-09-18	83	523
7911	09:20:00	11:00:00	2024-09-25	83	523
7912	09:20:00	11:00:00	2024-10-02	83	523
7913	09:20:00	11:00:00	2024-10-09	83	523
7914	09:20:00	11:00:00	2024-10-16	83	523
7915	09:20:00	11:00:00	2024-10-23	83	523
7916	09:20:00	11:00:00	2024-10-30	83	523
7917	09:20:00	11:00:00	2024-11-06	83	523
7918	09:20:00	11:00:00	2024-11-13	83	523
7919	09:20:00	11:00:00	2024-11-20	83	523
7920	09:20:00	11:00:00	2024-11-27	83	523
7921	09:20:00	11:00:00	2024-12-04	83	523
7922	09:20:00	11:00:00	2024-12-11	83	523
7923	09:20:00	11:00:00	2024-08-09	83	524
7924	09:20:00	11:00:00	2024-08-16	83	524
7925	09:20:00	11:00:00	2024-08-23	83	524
7926	09:20:00	11:00:00	2024-08-30	83	524
7927	09:20:00	11:00:00	2024-09-06	83	524
7928	09:20:00	11:00:00	2024-09-13	83	524
7929	09:20:00	11:00:00	2024-09-20	83	524
7930	09:20:00	11:00:00	2024-09-27	83	524
7931	09:20:00	11:00:00	2024-10-04	83	524
7932	09:20:00	11:00:00	2024-10-11	83	524
7933	09:20:00	11:00:00	2024-10-18	83	524
7934	09:20:00	11:00:00	2024-10-25	83	524
7935	09:20:00	11:00:00	2024-11-01	83	524
7936	09:20:00	11:00:00	2024-11-08	83	524
7937	09:20:00	11:00:00	2024-11-15	83	524
7938	09:20:00	11:00:00	2024-11-22	83	524
7939	09:20:00	11:00:00	2024-11-29	83	524
7940	09:20:00	11:00:00	2024-12-06	83	524
7979	09:20:00	11:00:00	2024-08-05	81	489
7980	09:20:00	11:00:00	2024-08-12	81	489
7981	09:20:00	11:00:00	2024-08-19	81	489
7982	09:20:00	11:00:00	2024-08-26	81	489
7983	09:20:00	11:00:00	2024-09-02	81	489
7984	09:20:00	11:00:00	2024-09-09	81	489
7985	09:20:00	11:00:00	2024-09-16	81	489
7986	09:20:00	11:00:00	2024-09-23	81	489
7987	09:20:00	11:00:00	2024-09-30	81	489
7988	09:20:00	11:00:00	2024-10-07	81	489
7989	09:20:00	11:00:00	2024-10-14	81	489
7990	09:20:00	11:00:00	2024-10-21	81	489
7991	09:20:00	11:00:00	2024-10-28	81	489
7992	09:20:00	11:00:00	2024-11-04	81	489
7993	09:20:00	11:00:00	2024-11-11	81	489
7994	09:20:00	11:00:00	2024-11-18	81	489
7995	09:20:00	11:00:00	2024-11-25	81	489
7996	09:20:00	11:00:00	2024-12-02	81	489
7997	09:20:00	11:00:00	2024-12-09	81	489
7998	10:10:00	11:50:00	2024-08-07	81	490
7999	10:10:00	11:50:00	2024-08-14	81	490
8000	10:10:00	11:50:00	2024-08-21	81	490
8001	10:10:00	11:50:00	2024-08-28	81	490
8002	10:10:00	11:50:00	2024-09-04	81	490
8003	10:10:00	11:50:00	2024-09-11	81	490
8004	10:10:00	11:50:00	2024-09-18	81	490
8005	10:10:00	11:50:00	2024-09-25	81	490
8006	10:10:00	11:50:00	2024-10-02	81	490
8007	10:10:00	11:50:00	2024-10-09	81	490
8008	10:10:00	11:50:00	2024-10-16	81	490
8009	10:10:00	11:50:00	2024-10-23	81	490
8010	10:10:00	11:50:00	2024-10-30	81	490
8011	10:10:00	11:50:00	2024-11-06	81	490
8012	10:10:00	11:50:00	2024-11-13	81	490
8013	10:10:00	11:50:00	2024-11-20	81	490
8014	10:10:00	11:50:00	2024-11-27	81	490
8015	10:10:00	11:50:00	2024-12-04	81	490
8016	10:10:00	11:50:00	2024-12-11	81	490
8017	13:10:00	16:40:00	2024-08-05	85	491
8018	13:10:00	16:40:00	2024-08-12	85	491
8019	13:10:00	16:40:00	2024-08-19	85	491
8020	13:10:00	16:40:00	2024-08-26	85	491
8021	13:10:00	16:40:00	2024-09-02	85	491
8022	13:10:00	16:40:00	2024-09-09	85	491
8023	13:10:00	16:40:00	2024-09-16	85	491
8024	13:10:00	16:40:00	2024-09-23	85	491
7892	09:20:00	11:00:00	2024-09-20	84	522
7893	09:20:00	11:00:00	2024-09-27	84	522
7894	09:20:00	11:00:00	2024-10-04	84	522
7895	09:20:00	11:00:00	2024-10-11	84	522
7896	09:20:00	11:00:00	2024-10-18	84	522
7897	09:20:00	11:00:00	2024-10-25	84	522
7898	09:20:00	11:00:00	2024-11-01	84	522
7899	09:20:00	11:00:00	2024-11-08	84	522
7900	09:20:00	11:00:00	2024-11-15	84	522
7901	09:20:00	11:00:00	2024-11-22	84	522
7902	09:20:00	11:00:00	2024-11-29	84	522
7903	09:20:00	11:00:00	2024-12-06	84	522
7941	10:10:00	11:50:00	2024-08-05	86	487
7942	10:10:00	11:50:00	2024-08-12	86	487
7943	10:10:00	11:50:00	2024-08-19	86	487
7944	10:10:00	11:50:00	2024-08-26	86	487
7945	10:10:00	11:50:00	2024-09-02	86	487
7946	10:10:00	11:50:00	2024-09-09	86	487
7947	10:10:00	11:50:00	2024-09-16	86	487
7948	10:10:00	11:50:00	2024-09-23	86	487
7949	10:10:00	11:50:00	2024-09-30	86	487
7950	10:10:00	11:50:00	2024-10-07	86	487
7951	10:10:00	11:50:00	2024-10-14	86	487
7952	10:10:00	11:50:00	2024-10-21	86	487
7953	10:10:00	11:50:00	2024-10-28	86	487
7954	10:10:00	11:50:00	2024-11-04	86	487
7955	10:10:00	11:50:00	2024-11-11	86	487
7956	10:10:00	11:50:00	2024-11-18	86	487
7957	10:10:00	11:50:00	2024-11-25	86	487
7958	10:10:00	11:50:00	2024-12-02	86	487
7959	10:10:00	11:50:00	2024-12-09	86	487
7960	10:10:00	11:50:00	2024-08-07	86	488
7961	10:10:00	11:50:00	2024-08-14	86	488
7962	10:10:00	11:50:00	2024-08-21	86	488
7963	10:10:00	11:50:00	2024-08-28	86	488
7964	10:10:00	11:50:00	2024-09-04	86	488
7965	10:10:00	11:50:00	2024-09-11	86	488
7966	10:10:00	11:50:00	2024-09-18	86	488
7967	10:10:00	11:50:00	2024-09-25	86	488
7968	10:10:00	11:50:00	2024-10-02	86	488
7969	10:10:00	11:50:00	2024-10-09	86	488
7970	10:10:00	11:50:00	2024-10-16	86	488
7971	10:10:00	11:50:00	2024-10-23	86	488
7972	10:10:00	11:50:00	2024-10-30	86	488
7973	10:10:00	11:50:00	2024-11-06	86	488
7974	10:10:00	11:50:00	2024-11-13	86	488
7975	10:10:00	11:50:00	2024-11-20	86	488
7976	10:10:00	11:50:00	2024-11-27	86	488
7977	10:10:00	11:50:00	2024-12-04	86	488
7978	10:10:00	11:50:00	2024-12-11	86	488
8093	13:10:00	14:50:00	2024-08-06	80	525
8094	13:10:00	14:50:00	2024-08-13	80	525
8095	13:10:00	14:50:00	2024-08-20	80	525
8096	13:10:00	14:50:00	2024-08-27	80	525
8097	13:10:00	14:50:00	2024-09-03	80	525
8098	13:10:00	14:50:00	2024-09-10	80	525
8099	13:10:00	14:50:00	2024-09-17	80	525
8100	13:10:00	14:50:00	2024-09-24	80	525
8101	13:10:00	14:50:00	2024-10-01	80	525
8102	13:10:00	14:50:00	2024-10-08	80	525
8103	13:10:00	14:50:00	2024-10-15	80	525
8104	13:10:00	14:50:00	2024-10-22	80	525
8105	13:10:00	14:50:00	2024-10-29	80	525
8106	13:10:00	14:50:00	2024-11-05	80	525
8107	13:10:00	14:50:00	2024-11-12	80	525
8108	13:10:00	14:50:00	2024-11-19	80	525
8109	13:10:00	14:50:00	2024-11-26	80	525
8110	13:10:00	14:50:00	2024-12-03	80	525
8111	13:10:00	14:50:00	2024-12-10	80	525
8112	13:10:00	14:50:00	2024-08-09	80	526
8113	13:10:00	14:50:00	2024-08-16	80	526
8114	13:10:00	14:50:00	2024-08-23	80	526
8115	13:10:00	14:50:00	2024-08-30	80	526
8116	13:10:00	14:50:00	2024-09-06	80	526
8117	13:10:00	14:50:00	2024-09-13	80	526
8118	13:10:00	14:50:00	2024-09-20	80	526
8119	13:10:00	14:50:00	2024-09-27	80	526
8120	13:10:00	14:50:00	2024-10-04	80	526
8121	13:10:00	14:50:00	2024-10-11	80	526
8122	13:10:00	14:50:00	2024-10-18	80	526
8123	13:10:00	14:50:00	2024-10-25	80	526
8124	13:10:00	14:50:00	2024-11-01	80	526
8125	13:10:00	14:50:00	2024-11-08	80	526
8126	13:10:00	14:50:00	2024-11-15	80	526
8127	13:10:00	14:50:00	2024-11-22	80	526
8128	13:10:00	14:50:00	2024-11-29	80	526
8129	13:10:00	14:50:00	2024-12-06	80	526
8025	13:10:00	16:40:00	2024-09-30	85	491
8026	13:10:00	16:40:00	2024-10-07	85	491
8027	13:10:00	16:40:00	2024-10-14	85	491
8028	13:10:00	16:40:00	2024-10-21	85	491
8029	13:10:00	16:40:00	2024-10-28	85	491
8030	13:10:00	16:40:00	2024-11-04	85	491
8031	13:10:00	16:40:00	2024-11-11	85	491
8032	13:10:00	16:40:00	2024-11-18	85	491
8033	13:10:00	16:40:00	2024-11-25	85	491
8034	13:10:00	16:40:00	2024-12-02	85	491
8035	13:10:00	16:40:00	2024-12-09	85	491
8036	13:10:00	16:40:00	2024-08-05	85	492
8037	13:10:00	16:40:00	2024-08-12	85	492
8038	13:10:00	16:40:00	2024-08-19	85	492
8039	13:10:00	16:40:00	2024-08-26	85	492
8040	13:10:00	16:40:00	2024-09-02	85	492
8041	13:10:00	16:40:00	2024-09-09	85	492
8042	13:10:00	16:40:00	2024-09-16	85	492
8043	13:10:00	16:40:00	2024-09-23	85	492
8044	13:10:00	16:40:00	2024-09-30	85	492
8045	13:10:00	16:40:00	2024-10-07	85	492
8046	13:10:00	16:40:00	2024-10-14	85	492
8047	13:10:00	16:40:00	2024-10-21	85	492
8048	13:10:00	16:40:00	2024-10-28	85	492
8049	13:10:00	16:40:00	2024-11-04	85	492
8050	13:10:00	16:40:00	2024-11-11	85	492
8051	13:10:00	16:40:00	2024-11-18	85	492
8052	13:10:00	16:40:00	2024-11-25	85	492
8053	13:10:00	16:40:00	2024-12-02	85	492
8054	13:10:00	16:40:00	2024-12-09	85	492
8055	13:10:00	16:40:00	2024-08-07	85	493
8056	13:10:00	16:40:00	2024-08-14	85	493
8057	13:10:00	16:40:00	2024-08-21	85	493
8058	13:10:00	16:40:00	2024-08-28	85	493
8059	13:10:00	16:40:00	2024-09-04	85	493
8060	13:10:00	16:40:00	2024-09-11	85	493
8061	13:10:00	16:40:00	2024-09-18	85	493
8062	13:10:00	16:40:00	2024-09-25	85	493
8063	13:10:00	16:40:00	2024-10-02	85	493
8064	13:10:00	16:40:00	2024-10-09	85	493
8065	13:10:00	16:40:00	2024-10-16	85	493
8066	13:10:00	16:40:00	2024-10-23	85	493
8067	13:10:00	16:40:00	2024-10-30	85	493
8068	13:10:00	16:40:00	2024-11-06	85	493
8069	13:10:00	16:40:00	2024-11-13	85	493
8070	13:10:00	16:40:00	2024-11-20	85	493
8071	13:10:00	16:40:00	2024-11-27	85	493
8072	13:10:00	16:40:00	2024-12-04	85	493
8073	13:10:00	16:40:00	2024-12-11	85	493
8074	13:10:00	16:40:00	2024-08-07	85	494
8075	13:10:00	16:40:00	2024-08-14	85	494
8076	13:10:00	16:40:00	2024-08-21	85	494
8077	13:10:00	16:40:00	2024-08-28	85	494
8078	13:10:00	16:40:00	2024-09-04	85	494
8079	13:10:00	16:40:00	2024-09-11	85	494
8080	13:10:00	16:40:00	2024-09-18	85	494
8081	13:10:00	16:40:00	2024-09-25	85	494
8082	13:10:00	16:40:00	2024-10-02	85	494
8083	13:10:00	16:40:00	2024-10-09	85	494
8084	13:10:00	16:40:00	2024-10-16	85	494
8085	13:10:00	16:40:00	2024-10-23	85	494
8086	13:10:00	16:40:00	2024-10-30	85	494
8087	13:10:00	16:40:00	2024-11-06	85	494
8088	13:10:00	16:40:00	2024-11-13	85	494
8089	13:10:00	16:40:00	2024-11-20	85	494
8090	13:10:00	16:40:00	2024-11-27	85	494
8091	13:10:00	16:40:00	2024-12-04	85	494
8092	13:10:00	16:40:00	2024-12-11	85	494
8130	13:10:00	14:50:00	2024-08-06	81	527
8131	13:10:00	14:50:00	2024-08-13	81	527
8132	13:10:00	14:50:00	2024-08-20	81	527
8133	13:10:00	14:50:00	2024-08-27	81	527
8134	13:10:00	14:50:00	2024-09-03	81	527
8135	13:10:00	14:50:00	2024-09-10	81	527
8136	13:10:00	14:50:00	2024-09-17	81	527
8137	13:10:00	14:50:00	2024-09-24	81	527
8138	13:10:00	14:50:00	2024-10-01	81	527
8139	13:10:00	14:50:00	2024-10-08	81	527
8140	13:10:00	14:50:00	2024-10-15	81	527
8141	13:10:00	14:50:00	2024-10-22	81	527
8142	13:10:00	14:50:00	2024-10-29	81	527
8143	13:10:00	14:50:00	2024-11-05	81	527
8144	13:10:00	14:50:00	2024-11-12	81	527
8145	13:10:00	14:50:00	2024-11-19	81	527
8146	13:10:00	14:50:00	2024-11-26	81	527
8147	13:10:00	14:50:00	2024-12-03	81	527
8148	13:10:00	14:50:00	2024-12-10	81	527
8149	13:10:00	14:50:00	2024-08-09	81	528
8150	13:10:00	14:50:00	2024-08-16	81	528
8151	13:10:00	14:50:00	2024-08-23	81	528
8152	13:10:00	14:50:00	2024-08-30	81	528
8153	13:10:00	14:50:00	2024-09-06	81	528
8154	13:10:00	14:50:00	2024-09-13	81	528
8155	13:10:00	14:50:00	2024-09-20	81	528
8156	13:10:00	14:50:00	2024-09-27	81	528
8157	13:10:00	14:50:00	2024-10-04	81	528
8158	13:10:00	14:50:00	2024-10-11	81	528
8159	13:10:00	14:50:00	2024-10-18	81	528
8160	13:10:00	14:50:00	2024-10-25	81	528
8161	13:10:00	14:50:00	2024-11-01	81	528
8162	13:10:00	14:50:00	2024-11-08	81	528
8163	13:10:00	14:50:00	2024-11-15	81	528
8164	13:10:00	14:50:00	2024-11-22	81	528
8165	13:10:00	14:50:00	2024-11-29	81	528
8166	13:10:00	14:50:00	2024-12-06	81	528
8167	13:10:00	16:40:00	2024-08-06	78	529
8168	13:10:00	16:40:00	2024-08-13	78	529
8169	13:10:00	16:40:00	2024-08-20	78	529
8170	13:10:00	16:40:00	2024-08-27	78	529
8171	13:10:00	16:40:00	2024-09-03	78	529
8172	13:10:00	16:40:00	2024-09-10	78	529
8173	13:10:00	16:40:00	2024-09-17	78	529
8174	13:10:00	16:40:00	2024-09-24	78	529
8175	13:10:00	16:40:00	2024-10-01	78	529
8176	13:10:00	16:40:00	2024-10-08	78	529
8177	13:10:00	16:40:00	2024-10-15	78	529
8178	13:10:00	16:40:00	2024-10-22	78	529
8179	13:10:00	16:40:00	2024-10-29	78	529
8180	13:10:00	16:40:00	2024-11-05	78	529
8181	13:10:00	16:40:00	2024-11-12	78	529
8182	13:10:00	16:40:00	2024-11-19	78	529
8183	13:10:00	16:40:00	2024-11-26	78	529
8184	13:10:00	16:40:00	2024-12-03	78	529
8185	13:10:00	16:40:00	2024-12-10	78	529
8186	13:10:00	16:40:00	2024-08-06	78	530
8187	13:10:00	16:40:00	2024-08-13	78	530
8188	13:10:00	16:40:00	2024-08-20	78	530
8189	13:10:00	16:40:00	2024-08-27	78	530
8190	13:10:00	16:40:00	2024-09-03	78	530
8191	13:10:00	16:40:00	2024-09-10	78	530
8192	13:10:00	16:40:00	2024-09-17	78	530
8193	13:10:00	16:40:00	2024-09-24	78	530
8194	13:10:00	16:40:00	2024-10-01	78	530
8195	13:10:00	16:40:00	2024-10-08	78	530
8196	13:10:00	16:40:00	2024-10-15	78	530
8197	13:10:00	16:40:00	2024-10-22	78	530
8198	13:10:00	16:40:00	2024-10-29	78	530
8199	13:10:00	16:40:00	2024-11-05	78	530
8200	13:10:00	16:40:00	2024-11-12	78	530
8201	13:10:00	16:40:00	2024-11-19	78	530
8202	13:10:00	16:40:00	2024-11-26	78	530
8203	13:10:00	16:40:00	2024-12-03	78	530
8204	13:10:00	16:40:00	2024-12-10	78	530
8205	13:10:00	16:40:00	2024-08-07	78	531
8206	13:10:00	16:40:00	2024-08-14	78	531
8207	13:10:00	16:40:00	2024-08-21	78	531
8208	13:10:00	16:40:00	2024-08-28	78	531
8209	13:10:00	16:40:00	2024-09-04	78	531
8210	13:10:00	16:40:00	2024-09-11	78	531
8211	13:10:00	16:40:00	2024-09-18	78	531
8212	13:10:00	16:40:00	2024-09-25	78	531
8213	13:10:00	16:40:00	2024-10-02	78	531
8214	13:10:00	16:40:00	2024-10-09	78	531
8215	13:10:00	16:40:00	2024-10-16	78	531
8216	13:10:00	16:40:00	2024-10-23	78	531
8217	13:10:00	16:40:00	2024-10-30	78	531
8218	13:10:00	16:40:00	2024-11-06	78	531
8219	13:10:00	16:40:00	2024-11-13	78	531
8220	13:10:00	16:40:00	2024-11-20	78	531
8221	13:10:00	16:40:00	2024-11-27	78	531
8222	13:10:00	16:40:00	2024-12-04	78	531
8223	13:10:00	16:40:00	2024-12-11	78	531
8224	13:10:00	16:40:00	2024-08-07	78	532
8225	13:10:00	16:40:00	2024-08-14	78	532
8226	13:10:00	16:40:00	2024-08-21	78	532
8227	13:10:00	16:40:00	2024-08-28	78	532
8228	13:10:00	16:40:00	2024-09-04	78	532
8229	13:10:00	16:40:00	2024-09-11	78	532
8230	13:10:00	16:40:00	2024-09-18	78	532
8231	13:10:00	16:40:00	2024-09-25	78	532
8232	13:10:00	16:40:00	2024-10-02	78	532
8233	13:10:00	16:40:00	2024-10-09	78	532
8234	13:10:00	16:40:00	2024-10-16	78	532
8235	13:10:00	16:40:00	2024-10-23	78	532
8236	13:10:00	16:40:00	2024-10-30	78	532
8237	13:10:00	16:40:00	2024-11-06	78	532
8238	13:10:00	16:40:00	2024-11-13	78	532
8239	13:10:00	16:40:00	2024-11-20	78	532
8240	13:10:00	16:40:00	2024-11-27	78	532
8241	13:10:00	16:40:00	2024-12-04	78	532
8242	13:10:00	16:40:00	2024-12-11	78	532
8243	13:10:00	16:40:00	2024-08-05	78	533
8244	13:10:00	16:40:00	2024-08-12	78	533
8245	13:10:00	16:40:00	2024-08-19	78	533
8246	13:10:00	16:40:00	2024-08-26	78	533
8247	13:10:00	16:40:00	2024-09-02	78	533
8248	13:10:00	16:40:00	2024-09-09	78	533
8249	13:10:00	16:40:00	2024-09-16	78	533
8250	13:10:00	16:40:00	2024-09-23	78	533
8251	13:10:00	16:40:00	2024-09-30	78	533
8252	13:10:00	16:40:00	2024-10-07	78	533
8253	13:10:00	16:40:00	2024-10-14	78	533
8254	13:10:00	16:40:00	2024-10-21	78	533
8255	13:10:00	16:40:00	2024-10-28	78	533
8256	13:10:00	16:40:00	2024-11-04	78	533
8257	13:10:00	16:40:00	2024-11-11	78	533
8258	13:10:00	16:40:00	2024-11-18	78	533
8259	13:10:00	16:40:00	2024-11-25	78	533
8260	13:10:00	16:40:00	2024-12-02	78	533
8261	13:10:00	16:40:00	2024-12-09	78	533
8262	13:10:00	16:40:00	2024-08-08	78	534
8263	13:10:00	16:40:00	2024-08-15	78	534
8264	13:10:00	16:40:00	2024-08-22	78	534
8265	13:10:00	16:40:00	2024-08-29	78	534
8266	13:10:00	16:40:00	2024-09-05	78	534
8267	13:10:00	16:40:00	2024-09-12	78	534
8268	13:10:00	16:40:00	2024-09-19	78	534
8269	13:10:00	16:40:00	2024-09-26	78	534
8270	13:10:00	16:40:00	2024-10-03	78	534
8271	13:10:00	16:40:00	2024-10-10	78	534
8272	13:10:00	16:40:00	2024-10-17	78	534
8273	13:10:00	16:40:00	2024-10-24	78	534
8274	13:10:00	16:40:00	2024-10-31	78	534
8275	13:10:00	16:40:00	2024-11-07	78	534
8276	13:10:00	16:40:00	2024-11-14	78	534
8277	13:10:00	16:40:00	2024-11-21	78	534
8278	13:10:00	16:40:00	2024-11-28	78	534
8279	13:10:00	16:40:00	2024-12-05	78	534
8280	13:10:00	16:40:00	2024-12-12	78	534
8281	09:20:00	11:00:00	2024-08-09	81	535
8282	09:20:00	11:00:00	2024-08-16	81	535
8283	09:20:00	11:00:00	2024-08-23	81	535
8284	09:20:00	11:00:00	2024-08-30	81	535
8285	09:20:00	11:00:00	2024-09-06	81	535
8286	09:20:00	11:00:00	2024-09-13	81	535
8287	09:20:00	11:00:00	2024-09-20	81	535
8288	09:20:00	11:00:00	2024-09-27	81	535
8289	09:20:00	11:00:00	2024-10-04	81	535
8290	09:20:00	11:00:00	2024-10-11	81	535
8291	09:20:00	11:00:00	2024-10-18	81	535
8292	09:20:00	11:00:00	2024-10-25	81	535
8293	09:20:00	11:00:00	2024-11-01	81	535
8294	09:20:00	11:00:00	2024-11-08	81	535
8295	09:20:00	11:00:00	2024-11-15	81	535
8296	09:20:00	11:00:00	2024-11-22	81	535
8297	09:20:00	11:00:00	2024-11-29	81	535
8298	09:20:00	11:00:00	2024-12-06	81	535
8299	15:00:00	18:30:00	2024-08-05	77	536
8300	15:00:00	18:30:00	2024-08-12	77	536
8301	15:00:00	18:30:00	2024-08-19	77	536
8302	15:00:00	18:30:00	2024-08-26	77	536
8303	15:00:00	18:30:00	2024-09-02	77	536
8304	15:00:00	18:30:00	2024-09-09	77	536
8305	15:00:00	18:30:00	2024-09-16	77	536
8306	15:00:00	18:30:00	2024-09-23	77	536
8307	15:00:00	18:30:00	2024-09-30	77	536
8308	15:00:00	18:30:00	2024-10-07	77	536
8309	15:00:00	18:30:00	2024-10-14	77	536
8310	15:00:00	18:30:00	2024-10-21	77	536
8311	15:00:00	18:30:00	2024-10-28	77	536
8312	15:00:00	18:30:00	2024-11-04	77	536
8313	15:00:00	18:30:00	2024-11-11	77	536
8314	15:00:00	18:30:00	2024-11-18	77	536
8315	15:00:00	18:30:00	2024-11-25	77	536
8316	15:00:00	18:30:00	2024-12-02	77	536
8317	15:00:00	18:30:00	2024-12-09	77	536
8318	15:00:00	18:30:00	2024-08-05	77	537
8319	15:00:00	18:30:00	2024-08-12	77	537
8320	15:00:00	18:30:00	2024-08-19	77	537
8321	15:00:00	18:30:00	2024-08-26	77	537
8322	15:00:00	18:30:00	2024-09-02	77	537
8323	15:00:00	18:30:00	2024-09-09	77	537
8324	15:00:00	18:30:00	2024-09-16	77	537
8325	15:00:00	18:30:00	2024-09-23	77	537
8326	15:00:00	18:30:00	2024-09-30	77	537
8327	15:00:00	18:30:00	2024-10-07	77	537
8328	15:00:00	18:30:00	2024-10-14	77	537
8329	15:00:00	18:30:00	2024-10-21	77	537
8330	15:00:00	18:30:00	2024-10-28	77	537
8331	15:00:00	18:30:00	2024-11-04	77	537
8332	15:00:00	18:30:00	2024-11-11	77	537
8333	15:00:00	18:30:00	2024-11-18	77	537
8334	15:00:00	18:30:00	2024-11-25	77	537
8335	15:00:00	18:30:00	2024-12-02	77	537
8336	15:00:00	18:30:00	2024-12-09	77	537
8337	07:30:00	10:10:00	2024-08-08	81	538
8338	07:30:00	10:10:00	2024-08-15	81	538
8339	07:30:00	10:10:00	2024-08-22	81	538
8340	07:30:00	10:10:00	2024-08-29	81	538
8341	07:30:00	10:10:00	2024-09-05	81	538
8342	07:30:00	10:10:00	2024-09-12	81	538
8343	07:30:00	10:10:00	2024-09-19	81	538
8344	07:30:00	10:10:00	2024-09-26	81	538
8345	07:30:00	10:10:00	2024-10-03	81	538
8346	07:30:00	10:10:00	2024-10-10	81	538
8347	07:30:00	10:10:00	2024-10-17	81	538
8348	07:30:00	10:10:00	2024-10-24	81	538
8349	07:30:00	10:10:00	2024-10-31	81	538
8350	07:30:00	10:10:00	2024-11-07	81	538
8351	07:30:00	10:10:00	2024-11-14	81	538
8352	07:30:00	10:10:00	2024-11-21	81	538
8353	07:30:00	10:10:00	2024-11-28	81	538
8354	07:30:00	10:10:00	2024-12-05	81	538
8355	07:30:00	10:10:00	2024-12-12	81	538
8356	14:00:00	17:30:00	2024-08-06	85	539
8357	14:00:00	17:30:00	2024-08-13	85	539
8358	14:00:00	17:30:00	2024-08-20	85	539
8359	14:00:00	17:30:00	2024-08-27	85	539
8360	14:00:00	17:30:00	2024-09-03	85	539
8361	14:00:00	17:30:00	2024-09-10	85	539
8362	14:00:00	17:30:00	2024-09-17	85	539
8363	14:00:00	17:30:00	2024-09-24	85	539
8364	14:00:00	17:30:00	2024-10-01	85	539
8365	14:00:00	17:30:00	2024-10-08	85	539
8366	14:00:00	17:30:00	2024-10-15	85	539
8367	14:00:00	17:30:00	2024-10-22	85	539
8368	14:00:00	17:30:00	2024-10-29	85	539
8369	14:00:00	17:30:00	2024-11-05	85	539
8370	14:00:00	17:30:00	2024-11-12	85	539
8371	14:00:00	17:30:00	2024-11-19	85	539
8372	14:00:00	17:30:00	2024-11-26	85	539
8373	14:00:00	17:30:00	2024-12-03	85	539
8374	14:00:00	17:30:00	2024-12-10	85	539
8375	14:00:00	17:30:00	2024-08-06	85	540
8376	14:00:00	17:30:00	2024-08-13	85	540
8377	14:00:00	17:30:00	2024-08-20	85	540
8378	14:00:00	17:30:00	2024-08-27	85	540
8379	14:00:00	17:30:00	2024-09-03	85	540
8380	14:00:00	17:30:00	2024-09-10	85	540
8381	14:00:00	17:30:00	2024-09-17	85	540
8382	14:00:00	17:30:00	2024-09-24	85	540
8383	14:00:00	17:30:00	2024-10-01	85	540
8384	14:00:00	17:30:00	2024-10-08	85	540
8385	14:00:00	17:30:00	2024-10-15	85	540
8386	14:00:00	17:30:00	2024-10-22	85	540
8387	14:00:00	17:30:00	2024-10-29	85	540
8388	14:00:00	17:30:00	2024-11-05	85	540
8389	14:00:00	17:30:00	2024-11-12	85	540
8390	14:00:00	17:30:00	2024-11-19	85	540
8391	14:00:00	17:30:00	2024-11-26	85	540
8392	14:00:00	17:30:00	2024-12-03	85	540
8393	14:00:00	17:30:00	2024-12-10	85	540
8394	14:00:00	17:30:00	2024-08-08	85	541
8395	14:00:00	17:30:00	2024-08-15	85	541
8396	14:00:00	17:30:00	2024-08-22	85	541
8397	14:00:00	17:30:00	2024-08-29	85	541
8398	14:00:00	17:30:00	2024-09-05	85	541
8399	14:00:00	17:30:00	2024-09-12	85	541
8400	14:00:00	17:30:00	2024-09-19	85	541
8401	14:00:00	17:30:00	2024-09-26	85	541
8402	14:00:00	17:30:00	2024-10-03	85	541
8403	14:00:00	17:30:00	2024-10-10	85	541
8404	14:00:00	17:30:00	2024-10-17	85	541
8405	14:00:00	17:30:00	2024-10-24	85	541
8406	14:00:00	17:30:00	2024-10-31	85	541
8407	14:00:00	17:30:00	2024-11-07	85	541
8408	14:00:00	17:30:00	2024-11-14	85	541
8409	14:00:00	17:30:00	2024-11-21	85	541
8410	14:00:00	17:30:00	2024-11-28	85	541
8411	14:00:00	17:30:00	2024-12-05	85	541
8412	14:00:00	17:30:00	2024-12-12	85	541
8413	14:00:00	17:30:00	2024-08-08	85	542
8414	14:00:00	17:30:00	2024-08-15	85	542
8415	14:00:00	17:30:00	2024-08-22	85	542
8416	14:00:00	17:30:00	2024-08-29	85	542
8417	14:00:00	17:30:00	2024-09-05	85	542
8418	14:00:00	17:30:00	2024-09-12	85	542
8419	14:00:00	17:30:00	2024-09-19	85	542
8420	14:00:00	17:30:00	2024-09-26	85	542
8421	14:00:00	17:30:00	2024-10-03	85	542
8422	14:00:00	17:30:00	2024-10-10	85	542
8423	14:00:00	17:30:00	2024-10-17	85	542
8424	14:00:00	17:30:00	2024-10-24	85	542
8425	14:00:00	17:30:00	2024-10-31	85	542
8426	14:00:00	17:30:00	2024-11-07	85	542
8427	14:00:00	17:30:00	2024-11-14	85	542
8428	14:00:00	17:30:00	2024-11-21	85	542
8429	14:00:00	17:30:00	2024-11-28	85	542
8430	14:00:00	17:30:00	2024-12-05	85	542
8431	14:00:00	17:30:00	2024-12-12	85	542
8469	09:20:00	11:00:00	2024-08-07	78	559
8470	09:20:00	11:00:00	2024-08-14	78	559
8471	09:20:00	11:00:00	2024-08-21	78	559
8472	09:20:00	11:00:00	2024-08-28	78	559
8473	09:20:00	11:00:00	2024-09-04	78	559
8474	09:20:00	11:00:00	2024-09-11	78	559
8475	09:20:00	11:00:00	2024-09-18	78	559
8476	09:20:00	11:00:00	2024-09-25	78	559
8477	09:20:00	11:00:00	2024-10-02	78	559
8478	09:20:00	11:00:00	2024-10-09	78	559
8479	09:20:00	11:00:00	2024-10-16	78	559
8480	09:20:00	11:00:00	2024-10-23	78	559
8481	09:20:00	11:00:00	2024-10-30	78	559
8482	09:20:00	11:00:00	2024-11-06	78	559
8483	09:20:00	11:00:00	2024-11-13	78	559
8484	09:20:00	11:00:00	2024-11-20	78	559
8485	09:20:00	11:00:00	2024-11-27	78	559
8486	09:20:00	11:00:00	2024-12-04	78	559
8487	09:20:00	11:00:00	2024-12-11	78	559
8488	07:30:00	09:10:00	2024-08-09	78	560
8489	07:30:00	09:10:00	2024-08-16	78	560
8490	07:30:00	09:10:00	2024-08-23	78	560
8491	07:30:00	09:10:00	2024-08-30	78	560
8492	07:30:00	09:10:00	2024-09-06	78	560
8493	07:30:00	09:10:00	2024-09-13	78	560
8494	07:30:00	09:10:00	2024-09-20	78	560
8495	07:30:00	09:10:00	2024-09-27	78	560
8496	07:30:00	09:10:00	2024-10-04	78	560
8497	07:30:00	09:10:00	2024-10-11	78	560
8498	07:30:00	09:10:00	2024-10-18	78	560
8499	07:30:00	09:10:00	2024-10-25	78	560
8500	07:30:00	09:10:00	2024-11-01	78	560
8501	07:30:00	09:10:00	2024-11-08	78	560
8502	07:30:00	09:10:00	2024-11-15	78	560
8503	07:30:00	09:10:00	2024-11-22	78	560
8504	07:30:00	09:10:00	2024-11-29	78	560
8505	07:30:00	09:10:00	2024-12-06	78	560
8748	16:50:00	18:30:00	2024-08-09	79	565
8749	16:50:00	18:30:00	2024-08-16	79	565
8750	16:50:00	18:30:00	2024-08-23	79	565
8751	16:50:00	18:30:00	2024-08-30	79	565
8752	16:50:00	18:30:00	2024-09-06	79	565
8753	16:50:00	18:30:00	2024-09-13	79	565
8754	16:50:00	18:30:00	2024-09-20	79	565
8755	16:50:00	18:30:00	2024-09-27	79	565
8756	16:50:00	18:30:00	2024-10-04	79	565
8757	16:50:00	18:30:00	2024-10-11	79	565
8758	16:50:00	18:30:00	2024-10-18	79	565
8759	16:50:00	18:30:00	2024-10-25	79	565
8760	16:50:00	18:30:00	2024-11-01	79	565
8761	16:50:00	18:30:00	2024-11-08	79	565
8762	16:50:00	18:30:00	2024-11-15	79	565
8763	16:50:00	18:30:00	2024-11-22	79	565
8764	16:50:00	18:30:00	2024-11-29	79	565
8765	16:50:00	18:30:00	2024-12-06	79	565
8856	09:20:00	11:00:00	2024-08-05	87	566
8857	09:20:00	11:00:00	2024-08-12	87	566
8858	09:20:00	11:00:00	2024-08-19	87	566
8859	09:20:00	11:00:00	2024-08-26	87	566
8860	09:20:00	11:00:00	2024-09-02	87	566
8861	09:20:00	11:00:00	2024-09-09	87	566
8862	09:20:00	11:00:00	2024-09-16	87	566
8863	09:20:00	11:00:00	2024-09-23	87	566
8864	09:20:00	11:00:00	2024-09-30	87	566
8865	09:20:00	11:00:00	2024-10-07	87	566
8866	09:20:00	11:00:00	2024-10-14	87	566
8867	09:20:00	11:00:00	2024-10-21	87	566
8868	09:20:00	11:00:00	2024-10-28	87	566
8869	09:20:00	11:00:00	2024-11-04	87	566
8870	09:20:00	11:00:00	2024-11-11	87	566
8871	09:20:00	11:00:00	2024-11-18	87	566
8872	09:20:00	11:00:00	2024-11-25	87	566
8873	09:20:00	11:00:00	2024-12-02	87	566
8874	09:20:00	11:00:00	2024-12-09	87	566
8950	13:10:00	14:50:00	2024-08-08	87	572
8951	13:10:00	14:50:00	2024-08-15	87	572
8952	13:10:00	14:50:00	2024-08-22	87	572
8953	13:10:00	14:50:00	2024-08-29	87	572
8954	13:10:00	14:50:00	2024-09-05	87	572
8955	13:10:00	14:50:00	2024-09-12	87	572
8956	13:10:00	14:50:00	2024-09-19	87	572
8957	13:10:00	14:50:00	2024-09-26	87	572
8958	13:10:00	14:50:00	2024-10-03	87	572
8959	13:10:00	14:50:00	2024-10-10	87	572
8960	13:10:00	14:50:00	2024-10-17	87	572
8961	13:10:00	14:50:00	2024-10-24	87	572
8962	13:10:00	14:50:00	2024-10-31	87	572
8963	13:10:00	14:50:00	2024-11-07	87	572
8964	13:10:00	14:50:00	2024-11-14	87	572
8965	13:10:00	14:50:00	2024-11-21	87	572
8966	13:10:00	14:50:00	2024-11-28	87	572
8967	13:10:00	14:50:00	2024-12-05	87	572
9099	07:30:00	11:00:00	2024-08-09	88	580
9100	07:30:00	11:00:00	2024-08-16	88	580
9101	07:30:00	11:00:00	2024-08-23	88	580
9102	07:30:00	11:00:00	2024-08-30	88	580
9103	07:30:00	11:00:00	2024-09-06	88	580
9104	07:30:00	11:00:00	2024-09-13	88	580
9105	07:30:00	11:00:00	2024-09-20	88	580
9106	07:30:00	11:00:00	2024-09-27	88	580
9107	07:30:00	11:00:00	2024-10-04	88	580
9108	07:30:00	11:00:00	2024-10-11	88	580
9109	07:30:00	11:00:00	2024-10-18	88	580
9110	07:30:00	11:00:00	2024-10-25	88	580
9111	07:30:00	11:00:00	2024-11-01	88	580
9112	07:30:00	11:00:00	2024-11-08	88	580
9113	07:30:00	11:00:00	2024-11-15	88	580
9114	07:30:00	11:00:00	2024-11-22	88	580
9115	07:30:00	11:00:00	2024-11-29	88	580
9116	07:30:00	11:00:00	2024-12-06	88	580
8432	13:10:00	14:50:00	2024-08-09	76	543
8433	13:10:00	14:50:00	2024-08-16	76	543
8434	13:10:00	14:50:00	2024-08-23	76	543
8435	13:10:00	14:50:00	2024-08-30	76	543
8436	13:10:00	14:50:00	2024-09-06	76	543
8437	13:10:00	14:50:00	2024-09-13	76	543
8438	13:10:00	14:50:00	2024-09-20	76	543
8439	13:10:00	14:50:00	2024-09-27	76	543
8440	13:10:00	14:50:00	2024-10-04	76	543
8441	13:10:00	14:50:00	2024-10-11	76	543
8442	13:10:00	14:50:00	2024-10-18	76	543
8443	13:10:00	14:50:00	2024-10-25	76	543
8444	13:10:00	14:50:00	2024-11-01	76	543
8445	13:10:00	14:50:00	2024-11-08	76	543
8446	13:10:00	14:50:00	2024-11-15	76	543
8447	13:10:00	14:50:00	2024-11-22	76	543
8448	13:10:00	14:50:00	2024-11-29	76	543
8449	13:10:00	14:50:00	2024-12-06	76	543
8525	07:30:00	11:00:00	2024-08-10	84	553
8526	07:30:00	11:00:00	2024-08-17	84	553
8527	07:30:00	11:00:00	2024-08-24	84	553
8528	07:30:00	11:00:00	2024-08-31	84	553
8529	07:30:00	11:00:00	2024-09-07	84	553
8530	07:30:00	11:00:00	2024-09-14	84	553
8531	07:30:00	11:00:00	2024-09-21	84	553
8532	07:30:00	11:00:00	2024-09-28	84	553
8533	07:30:00	11:00:00	2024-10-05	84	553
8534	07:30:00	11:00:00	2024-10-12	84	553
8535	07:30:00	11:00:00	2024-10-19	84	553
8536	07:30:00	11:00:00	2024-10-26	84	553
8537	07:30:00	11:00:00	2024-11-02	84	553
8538	07:30:00	11:00:00	2024-11-09	84	553
8539	07:30:00	11:00:00	2024-11-16	84	553
8540	07:30:00	11:00:00	2024-11-23	84	553
8541	07:30:00	11:00:00	2024-11-30	84	553
8542	07:30:00	11:00:00	2024-12-07	84	553
8580	08:20:00	12:00:00	2024-08-08	84	550
8581	08:20:00	12:00:00	2024-08-15	84	550
8582	08:20:00	12:00:00	2024-08-22	84	550
8583	08:20:00	12:00:00	2024-08-29	84	550
8584	08:20:00	12:00:00	2024-09-05	84	550
8585	08:20:00	12:00:00	2024-09-12	84	550
8586	08:20:00	12:00:00	2024-09-19	84	550
8587	08:20:00	12:00:00	2024-09-26	84	550
8588	08:20:00	12:00:00	2024-10-03	84	550
8589	08:20:00	12:00:00	2024-10-10	84	550
8590	08:20:00	12:00:00	2024-10-17	84	550
8591	08:20:00	12:00:00	2024-10-24	84	550
8592	08:20:00	12:00:00	2024-10-31	84	550
8593	08:20:00	12:00:00	2024-11-07	84	550
8594	08:20:00	12:00:00	2024-11-14	84	550
8595	08:20:00	12:00:00	2024-11-21	84	550
8596	08:20:00	12:00:00	2024-11-28	84	550
8597	08:20:00	12:00:00	2024-12-05	84	550
8598	08:20:00	12:00:00	2024-12-12	84	550
8730	16:50:00	18:30:00	2024-08-09	80	564
8731	16:50:00	18:30:00	2024-08-16	80	564
8732	16:50:00	18:30:00	2024-08-23	80	564
8733	16:50:00	18:30:00	2024-08-30	80	564
8734	16:50:00	18:30:00	2024-09-06	80	564
8735	16:50:00	18:30:00	2024-09-13	80	564
8736	16:50:00	18:30:00	2024-09-20	80	564
8737	16:50:00	18:30:00	2024-09-27	80	564
8738	16:50:00	18:30:00	2024-10-04	80	564
8739	16:50:00	18:30:00	2024-10-11	80	564
8740	16:50:00	18:30:00	2024-10-18	80	564
8741	16:50:00	18:30:00	2024-10-25	80	564
8742	16:50:00	18:30:00	2024-11-01	80	564
8743	16:50:00	18:30:00	2024-11-08	80	564
8744	16:50:00	18:30:00	2024-11-15	80	564
8745	16:50:00	18:30:00	2024-11-22	80	564
8746	16:50:00	18:30:00	2024-11-29	80	564
8747	16:50:00	18:30:00	2024-12-06	80	564
8932	15:00:00	16:40:00	2024-08-08	87	573
8933	15:00:00	16:40:00	2024-08-15	87	573
8934	15:00:00	16:40:00	2024-08-22	87	573
8935	15:00:00	16:40:00	2024-08-29	87	573
8936	15:00:00	16:40:00	2024-09-05	87	573
8937	15:00:00	16:40:00	2024-09-12	87	573
8938	15:00:00	16:40:00	2024-09-19	87	573
8939	15:00:00	16:40:00	2024-09-26	87	573
8940	15:00:00	16:40:00	2024-10-03	87	573
8941	15:00:00	16:40:00	2024-10-10	87	573
8942	15:00:00	16:40:00	2024-10-17	87	573
8943	15:00:00	16:40:00	2024-10-24	87	573
8944	15:00:00	16:40:00	2024-10-31	87	573
8945	15:00:00	16:40:00	2024-11-07	87	573
8946	15:00:00	16:40:00	2024-11-14	87	573
8947	15:00:00	16:40:00	2024-11-21	87	573
8948	15:00:00	16:40:00	2024-11-28	87	573
8949	15:00:00	16:40:00	2024-12-05	87	573
8986	08:20:00	10:10:00	2024-08-09	87	568
8987	08:20:00	10:10:00	2024-08-16	87	568
8988	08:20:00	10:10:00	2024-08-23	87	568
8989	08:20:00	10:10:00	2024-08-30	87	568
8990	08:20:00	10:10:00	2024-09-06	87	568
8991	08:20:00	10:10:00	2024-09-13	87	568
8992	08:20:00	10:10:00	2024-09-20	87	568
8993	08:20:00	10:10:00	2024-09-27	87	568
8994	08:20:00	10:10:00	2024-10-04	87	568
8995	08:20:00	10:10:00	2024-10-11	87	568
8996	08:20:00	10:10:00	2024-10-18	87	568
8997	08:20:00	10:10:00	2024-10-25	87	568
8998	08:20:00	10:10:00	2024-11-01	87	568
8999	08:20:00	10:10:00	2024-11-08	87	568
9000	08:20:00	10:10:00	2024-11-15	87	568
9001	08:20:00	10:10:00	2024-11-22	87	568
9002	08:20:00	10:10:00	2024-11-29	87	568
9003	08:20:00	10:10:00	2024-12-06	87	568
8450	07:30:00	09:10:00	2024-08-06	84	544
8451	07:30:00	09:10:00	2024-08-13	84	544
8452	07:30:00	09:10:00	2024-08-20	84	544
8453	07:30:00	09:10:00	2024-08-27	84	544
8454	07:30:00	09:10:00	2024-09-03	84	544
8455	07:30:00	09:10:00	2024-09-10	84	544
8456	07:30:00	09:10:00	2024-09-17	84	544
8457	07:30:00	09:10:00	2024-09-24	84	544
8458	07:30:00	09:10:00	2024-10-01	84	544
8459	07:30:00	09:10:00	2024-10-08	84	544
8460	07:30:00	09:10:00	2024-10-15	84	544
8461	07:30:00	09:10:00	2024-10-22	84	544
8462	07:30:00	09:10:00	2024-10-29	84	544
8463	07:30:00	09:10:00	2024-11-05	84	544
8464	07:30:00	09:10:00	2024-11-12	84	544
8465	07:30:00	09:10:00	2024-11-19	84	544
8466	07:30:00	09:10:00	2024-11-26	84	544
8467	07:30:00	09:10:00	2024-12-03	84	544
8468	07:30:00	09:10:00	2024-12-10	84	544
8599	16:50:00	18:30:00	2024-08-09	81	551
8600	16:50:00	18:30:00	2024-08-16	81	551
8601	16:50:00	18:30:00	2024-08-23	81	551
8602	16:50:00	18:30:00	2024-08-30	81	551
8603	16:50:00	18:30:00	2024-09-06	81	551
8604	16:50:00	18:30:00	2024-09-13	81	551
8605	16:50:00	18:30:00	2024-09-20	81	551
8606	16:50:00	18:30:00	2024-09-27	81	551
8607	16:50:00	18:30:00	2024-10-04	81	551
8608	16:50:00	18:30:00	2024-10-11	81	551
8609	16:50:00	18:30:00	2024-10-18	81	551
8610	16:50:00	18:30:00	2024-10-25	81	551
8611	16:50:00	18:30:00	2024-11-01	81	551
8612	16:50:00	18:30:00	2024-11-08	81	551
8613	16:50:00	18:30:00	2024-11-15	81	551
8614	16:50:00	18:30:00	2024-11-22	81	551
8615	16:50:00	18:30:00	2024-11-29	81	551
8616	16:50:00	18:30:00	2024-12-06	81	551
8692	14:00:00	17:30:00	2024-08-06	79	557
8693	14:00:00	17:30:00	2024-08-13	79	557
8694	14:00:00	17:30:00	2024-08-20	79	557
8695	14:00:00	17:30:00	2024-08-27	79	557
8696	14:00:00	17:30:00	2024-09-03	79	557
8697	14:00:00	17:30:00	2024-09-10	79	557
8698	14:00:00	17:30:00	2024-09-17	79	557
8699	14:00:00	17:30:00	2024-09-24	79	557
8700	14:00:00	17:30:00	2024-10-01	79	557
8701	14:00:00	17:30:00	2024-10-08	79	557
8702	14:00:00	17:30:00	2024-10-15	79	557
8703	14:00:00	17:30:00	2024-10-22	79	557
8704	14:00:00	17:30:00	2024-10-29	79	557
8705	14:00:00	17:30:00	2024-11-05	79	557
8706	14:00:00	17:30:00	2024-11-12	79	557
8707	14:00:00	17:30:00	2024-11-19	79	557
8708	14:00:00	17:30:00	2024-11-26	79	557
8709	14:00:00	17:30:00	2024-12-03	79	557
8710	14:00:00	17:30:00	2024-12-10	79	557
8711	09:20:00	12:50:00	2024-08-08	80	558
8712	09:20:00	12:50:00	2024-08-15	80	558
8713	09:20:00	12:50:00	2024-08-22	80	558
8714	09:20:00	12:50:00	2024-08-29	80	558
8715	09:20:00	12:50:00	2024-09-05	80	558
8716	09:20:00	12:50:00	2024-09-12	80	558
8717	09:20:00	12:50:00	2024-09-19	80	558
8718	09:20:00	12:50:00	2024-09-26	80	558
8719	09:20:00	12:50:00	2024-10-03	80	558
8720	09:20:00	12:50:00	2024-10-10	80	558
8721	09:20:00	12:50:00	2024-10-17	80	558
8722	09:20:00	12:50:00	2024-10-24	80	558
8723	09:20:00	12:50:00	2024-10-31	80	558
8724	09:20:00	12:50:00	2024-11-07	80	558
8725	09:20:00	12:50:00	2024-11-14	80	558
8726	09:20:00	12:50:00	2024-11-21	80	558
8727	09:20:00	12:50:00	2024-11-28	80	558
8728	09:20:00	12:50:00	2024-12-05	80	558
8729	09:20:00	12:50:00	2024-12-12	80	558
8838	11:10:00	12:50:00	2024-08-09	80	562
8839	11:10:00	12:50:00	2024-08-16	80	562
8840	11:10:00	12:50:00	2024-08-23	80	562
8841	11:10:00	12:50:00	2024-08-30	80	562
8842	11:10:00	12:50:00	2024-09-06	80	562
8843	11:10:00	12:50:00	2024-09-13	80	562
8844	11:10:00	12:50:00	2024-09-20	80	562
8845	11:10:00	12:50:00	2024-09-27	80	562
8846	11:10:00	12:50:00	2024-10-04	80	562
8847	11:10:00	12:50:00	2024-10-11	80	562
8848	11:10:00	12:50:00	2024-10-18	80	562
8849	11:10:00	12:50:00	2024-10-25	80	562
8850	11:10:00	12:50:00	2024-11-01	80	562
8851	11:10:00	12:50:00	2024-11-08	80	562
8852	11:10:00	12:50:00	2024-11-15	80	562
8853	11:10:00	12:50:00	2024-11-22	80	562
8854	11:10:00	12:50:00	2024-11-29	80	562
8855	11:10:00	12:50:00	2024-12-06	80	562
8913	09:20:00	11:00:00	2024-08-06	87	567
8914	09:20:00	11:00:00	2024-08-13	87	567
8915	09:20:00	11:00:00	2024-08-20	87	567
8916	09:20:00	11:00:00	2024-08-27	87	567
8917	09:20:00	11:00:00	2024-09-03	87	567
8918	09:20:00	11:00:00	2024-09-10	87	567
8919	09:20:00	11:00:00	2024-09-17	87	567
8920	09:20:00	11:00:00	2024-09-24	87	567
8921	09:20:00	11:00:00	2024-10-01	87	567
8922	09:20:00	11:00:00	2024-10-08	87	567
8923	09:20:00	11:00:00	2024-10-15	87	567
8924	09:20:00	11:00:00	2024-10-22	87	567
8925	09:20:00	11:00:00	2024-10-29	87	567
8926	09:20:00	11:00:00	2024-11-05	87	567
8927	09:20:00	11:00:00	2024-11-12	87	567
8928	09:20:00	11:00:00	2024-11-19	87	567
8929	09:20:00	11:00:00	2024-11-26	87	567
8930	09:20:00	11:00:00	2024-12-03	87	567
8931	09:20:00	11:00:00	2024-12-10	87	567
9004	14:00:00	15:50:00	2024-08-05	87	577
9005	14:00:00	15:50:00	2024-08-12	87	577
9006	14:00:00	15:50:00	2024-08-19	87	577
9007	14:00:00	15:50:00	2024-08-26	87	577
9008	14:00:00	15:50:00	2024-09-02	87	577
9009	14:00:00	15:50:00	2024-09-09	87	577
9010	14:00:00	15:50:00	2024-09-16	87	577
9011	14:00:00	15:50:00	2024-09-23	87	577
8506	13:10:00	16:40:00	2024-08-06	84	552
8507	13:10:00	16:40:00	2024-08-13	84	552
8508	13:10:00	16:40:00	2024-08-20	84	552
8509	13:10:00	16:40:00	2024-08-27	84	552
8510	13:10:00	16:40:00	2024-09-03	84	552
8511	13:10:00	16:40:00	2024-09-10	84	552
8512	13:10:00	16:40:00	2024-09-17	84	552
8513	13:10:00	16:40:00	2024-09-24	84	552
8514	13:10:00	16:40:00	2024-10-01	84	552
8515	13:10:00	16:40:00	2024-10-08	84	552
8516	13:10:00	16:40:00	2024-10-15	84	552
8517	13:10:00	16:40:00	2024-10-22	84	552
8518	13:10:00	16:40:00	2024-10-29	84	552
8519	13:10:00	16:40:00	2024-11-05	84	552
8520	13:10:00	16:40:00	2024-11-12	84	552
8521	13:10:00	16:40:00	2024-11-19	84	552
8522	13:10:00	16:40:00	2024-11-26	84	552
8523	13:10:00	16:40:00	2024-12-03	84	552
8524	13:10:00	16:40:00	2024-12-10	84	552
8543	13:10:00	14:50:00	2024-08-08	76	548
8544	13:10:00	14:50:00	2024-08-15	76	548
8545	13:10:00	14:50:00	2024-08-22	76	548
8546	13:10:00	14:50:00	2024-08-29	76	548
8547	13:10:00	14:50:00	2024-09-05	76	548
8548	13:10:00	14:50:00	2024-09-12	76	548
8549	13:10:00	14:50:00	2024-09-19	76	548
8550	13:10:00	14:50:00	2024-09-26	76	548
8551	13:10:00	14:50:00	2024-10-03	76	548
8552	13:10:00	14:50:00	2024-10-10	76	548
8553	13:10:00	14:50:00	2024-10-17	76	548
8554	13:10:00	14:50:00	2024-10-24	76	548
8555	13:10:00	14:50:00	2024-10-31	76	548
8556	13:10:00	14:50:00	2024-11-07	76	548
8557	13:10:00	14:50:00	2024-11-14	76	548
8558	13:10:00	14:50:00	2024-11-21	76	548
8559	13:10:00	14:50:00	2024-11-28	76	548
8560	13:10:00	14:50:00	2024-12-05	76	548
8561	13:10:00	14:50:00	2024-12-12	76	548
8562	15:00:00	16:40:00	2024-08-09	76	549
8563	15:00:00	16:40:00	2024-08-16	76	549
8564	15:00:00	16:40:00	2024-08-23	76	549
8565	15:00:00	16:40:00	2024-08-30	76	549
8566	15:00:00	16:40:00	2024-09-06	76	549
8567	15:00:00	16:40:00	2024-09-13	76	549
8568	15:00:00	16:40:00	2024-09-20	76	549
8569	15:00:00	16:40:00	2024-09-27	76	549
8570	15:00:00	16:40:00	2024-10-04	76	549
8571	15:00:00	16:40:00	2024-10-11	76	549
8572	15:00:00	16:40:00	2024-10-18	76	549
8573	15:00:00	16:40:00	2024-10-25	76	549
8574	15:00:00	16:40:00	2024-11-01	76	549
8575	15:00:00	16:40:00	2024-11-08	76	549
8576	15:00:00	16:40:00	2024-11-15	76	549
8577	15:00:00	16:40:00	2024-11-22	76	549
8578	15:00:00	16:40:00	2024-11-29	76	549
8579	15:00:00	16:40:00	2024-12-06	76	549
8635	15:00:00	16:40:00	2024-08-05	81	554
8636	15:00:00	16:40:00	2024-08-12	81	554
8637	15:00:00	16:40:00	2024-08-19	81	554
8638	15:00:00	16:40:00	2024-08-26	81	554
8639	15:00:00	16:40:00	2024-09-02	81	554
8640	15:00:00	16:40:00	2024-09-09	81	554
8641	15:00:00	16:40:00	2024-09-16	81	554
8642	15:00:00	16:40:00	2024-09-23	81	554
8643	15:00:00	16:40:00	2024-09-30	81	554
8644	15:00:00	16:40:00	2024-10-07	81	554
8645	15:00:00	16:40:00	2024-10-14	81	554
8646	15:00:00	16:40:00	2024-10-21	81	554
8647	15:00:00	16:40:00	2024-10-28	81	554
8648	15:00:00	16:40:00	2024-11-04	81	554
8649	15:00:00	16:40:00	2024-11-11	81	554
8650	15:00:00	16:40:00	2024-11-18	81	554
8651	15:00:00	16:40:00	2024-11-25	81	554
8652	15:00:00	16:40:00	2024-12-02	81	554
8653	15:00:00	16:40:00	2024-12-09	81	554
8654	13:10:00	14:50:00	2024-08-07	81	555
8655	13:10:00	14:50:00	2024-08-14	81	555
8656	13:10:00	14:50:00	2024-08-21	81	555
8657	13:10:00	14:50:00	2024-08-28	81	555
8658	13:10:00	14:50:00	2024-09-04	81	555
8659	13:10:00	14:50:00	2024-09-11	81	555
8660	13:10:00	14:50:00	2024-09-18	81	555
8661	13:10:00	14:50:00	2024-09-25	81	555
8662	13:10:00	14:50:00	2024-10-02	81	555
8663	13:10:00	14:50:00	2024-10-09	81	555
8664	13:10:00	14:50:00	2024-10-16	81	555
8665	13:10:00	14:50:00	2024-10-23	81	555
8666	13:10:00	14:50:00	2024-10-30	81	555
8667	13:10:00	14:50:00	2024-11-06	81	555
8668	13:10:00	14:50:00	2024-11-13	81	555
8669	13:10:00	14:50:00	2024-11-20	81	555
8670	13:10:00	14:50:00	2024-11-27	81	555
8671	13:10:00	14:50:00	2024-12-04	81	555
8672	13:10:00	14:50:00	2024-12-11	81	555
8766	11:10:00	12:00:00	2024-08-10	84	545
8767	11:10:00	12:00:00	2024-08-17	84	545
8768	11:10:00	12:00:00	2024-08-24	84	545
8769	11:10:00	12:00:00	2024-08-31	84	545
8770	11:10:00	12:00:00	2024-09-07	84	545
8771	11:10:00	12:00:00	2024-09-14	84	545
8772	11:10:00	12:00:00	2024-09-21	84	545
8773	11:10:00	12:00:00	2024-09-28	84	545
8774	11:10:00	12:00:00	2024-10-05	84	545
8775	11:10:00	12:00:00	2024-10-12	84	545
8776	11:10:00	12:00:00	2024-10-19	84	545
8777	11:10:00	12:00:00	2024-10-26	84	545
8778	11:10:00	12:00:00	2024-11-02	84	545
8779	11:10:00	12:00:00	2024-11-09	84	545
8780	11:10:00	12:00:00	2024-11-16	84	545
8781	11:10:00	12:00:00	2024-11-23	84	545
8782	11:10:00	12:00:00	2024-11-30	84	545
8783	11:10:00	12:00:00	2024-12-07	84	545
8784	11:10:00	12:00:00	2024-08-09	79	546
8785	11:10:00	12:00:00	2024-08-16	79	546
8786	11:10:00	12:00:00	2024-08-23	79	546
8787	11:10:00	12:00:00	2024-08-30	79	546
8788	11:10:00	12:00:00	2024-09-06	79	546
8789	11:10:00	12:00:00	2024-09-13	79	546
8790	11:10:00	12:00:00	2024-09-20	79	546
8791	11:10:00	12:00:00	2024-09-27	79	546
8617	13:10:00	14:50:00	2024-08-09	84	563
8618	13:10:00	14:50:00	2024-08-16	84	563
8619	13:10:00	14:50:00	2024-08-23	84	563
8620	13:10:00	14:50:00	2024-08-30	84	563
8621	13:10:00	14:50:00	2024-09-06	84	563
8622	13:10:00	14:50:00	2024-09-13	84	563
8623	13:10:00	14:50:00	2024-09-20	84	563
8624	13:10:00	14:50:00	2024-09-27	84	563
8625	13:10:00	14:50:00	2024-10-04	84	563
8626	13:10:00	14:50:00	2024-10-11	84	563
8627	13:10:00	14:50:00	2024-10-18	84	563
8628	13:10:00	14:50:00	2024-10-25	84	563
8629	13:10:00	14:50:00	2024-11-01	84	563
8630	13:10:00	14:50:00	2024-11-08	84	563
8631	13:10:00	14:50:00	2024-11-15	84	563
8632	13:10:00	14:50:00	2024-11-22	84	563
8633	13:10:00	14:50:00	2024-11-29	84	563
8634	13:10:00	14:50:00	2024-12-06	84	563
8673	14:00:00	17:30:00	2024-08-06	79	556
8674	14:00:00	17:30:00	2024-08-13	79	556
8675	14:00:00	17:30:00	2024-08-20	79	556
8676	14:00:00	17:30:00	2024-08-27	79	556
8677	14:00:00	17:30:00	2024-09-03	79	556
8678	14:00:00	17:30:00	2024-09-10	79	556
8679	14:00:00	17:30:00	2024-09-17	79	556
8680	14:00:00	17:30:00	2024-09-24	79	556
8681	14:00:00	17:30:00	2024-10-01	79	556
8682	14:00:00	17:30:00	2024-10-08	79	556
8683	14:00:00	17:30:00	2024-10-15	79	556
8684	14:00:00	17:30:00	2024-10-22	79	556
8685	14:00:00	17:30:00	2024-10-29	79	556
8686	14:00:00	17:30:00	2024-11-05	79	556
8687	14:00:00	17:30:00	2024-11-12	79	556
8688	14:00:00	17:30:00	2024-11-19	79	556
8689	14:00:00	17:30:00	2024-11-26	79	556
8690	14:00:00	17:30:00	2024-12-03	79	556
8691	14:00:00	17:30:00	2024-12-10	79	556
8802	12:00:00	12:50:00	2024-08-09	79	547
8803	12:00:00	12:50:00	2024-08-16	79	547
8804	12:00:00	12:50:00	2024-08-23	79	547
8805	12:00:00	12:50:00	2024-08-30	79	547
8806	12:00:00	12:50:00	2024-09-06	79	547
8807	12:00:00	12:50:00	2024-09-13	79	547
8808	12:00:00	12:50:00	2024-09-20	79	547
8809	12:00:00	12:50:00	2024-09-27	79	547
8810	12:00:00	12:50:00	2024-10-04	79	547
8811	12:00:00	12:50:00	2024-10-11	79	547
8812	12:00:00	12:50:00	2024-10-18	79	547
8813	12:00:00	12:50:00	2024-10-25	79	547
8814	12:00:00	12:50:00	2024-11-01	79	547
8815	12:00:00	12:50:00	2024-11-08	79	547
8816	12:00:00	12:50:00	2024-11-15	79	547
8817	12:00:00	12:50:00	2024-11-22	79	547
8818	12:00:00	12:50:00	2024-11-29	79	547
8819	12:00:00	12:50:00	2024-12-06	79	547
8820	11:10:00	12:50:00	2024-08-09	80	561
8821	11:10:00	12:50:00	2024-08-16	80	561
8822	11:10:00	12:50:00	2024-08-23	80	561
8823	11:10:00	12:50:00	2024-08-30	80	561
8824	11:10:00	12:50:00	2024-09-06	80	561
8825	11:10:00	12:50:00	2024-09-13	80	561
8826	11:10:00	12:50:00	2024-09-20	80	561
8827	11:10:00	12:50:00	2024-09-27	80	561
8828	11:10:00	12:50:00	2024-10-04	80	561
8829	11:10:00	12:50:00	2024-10-11	80	561
8830	11:10:00	12:50:00	2024-10-18	80	561
8831	11:10:00	12:50:00	2024-10-25	80	561
8832	11:10:00	12:50:00	2024-11-01	80	561
8833	11:10:00	12:50:00	2024-11-08	80	561
8834	11:10:00	12:50:00	2024-11-15	80	561
8835	11:10:00	12:50:00	2024-11-22	80	561
8836	11:10:00	12:50:00	2024-11-29	80	561
8837	11:10:00	12:50:00	2024-12-06	80	561
8894	10:10:00	12:50:00	2024-08-07	87	571
8895	10:10:00	12:50:00	2024-08-14	87	571
8896	10:10:00	12:50:00	2024-08-21	87	571
8897	10:10:00	12:50:00	2024-08-28	87	571
8898	10:10:00	12:50:00	2024-09-04	87	571
8899	10:10:00	12:50:00	2024-09-11	87	571
8900	10:10:00	12:50:00	2024-09-18	87	571
8901	10:10:00	12:50:00	2024-09-25	87	571
8902	10:10:00	12:50:00	2024-10-02	87	571
8903	10:10:00	12:50:00	2024-10-09	87	571
8904	10:10:00	12:50:00	2024-10-16	87	571
8905	10:10:00	12:50:00	2024-10-23	87	571
8906	10:10:00	12:50:00	2024-10-30	87	571
8907	10:10:00	12:50:00	2024-11-06	87	571
8908	10:10:00	12:50:00	2024-11-13	87	571
8909	10:10:00	12:50:00	2024-11-20	87	571
8910	10:10:00	12:50:00	2024-11-27	87	571
8911	10:10:00	12:50:00	2024-12-04	87	571
8912	10:10:00	12:50:00	2024-12-11	87	571
9042	13:10:00	14:50:00	2024-08-06	87	575
9043	13:10:00	14:50:00	2024-08-13	87	575
9044	13:10:00	14:50:00	2024-08-20	87	575
9045	13:10:00	14:50:00	2024-08-27	87	575
9046	13:10:00	14:50:00	2024-09-03	87	575
9047	13:10:00	14:50:00	2024-09-10	87	575
9048	13:10:00	14:50:00	2024-09-17	87	575
9049	13:10:00	14:50:00	2024-09-24	87	575
9050	13:10:00	14:50:00	2024-10-01	87	575
9051	13:10:00	14:50:00	2024-10-08	87	575
9052	13:10:00	14:50:00	2024-10-15	87	575
9053	13:10:00	14:50:00	2024-10-22	87	575
9054	13:10:00	14:50:00	2024-10-29	87	575
9055	13:10:00	14:50:00	2024-11-05	87	575
9056	13:10:00	14:50:00	2024-11-12	87	575
9057	13:10:00	14:50:00	2024-11-19	87	575
9058	13:10:00	14:50:00	2024-11-26	87	575
9059	13:10:00	14:50:00	2024-12-03	87	575
9060	13:10:00	14:50:00	2024-12-10	87	575
9061	13:10:00	14:50:00	2024-08-07	87	576
9062	13:10:00	14:50:00	2024-08-14	87	576
9063	13:10:00	14:50:00	2024-08-21	87	576
9064	13:10:00	14:50:00	2024-08-28	87	576
9065	13:10:00	14:50:00	2024-09-04	87	576
9066	13:10:00	14:50:00	2024-09-11	87	576
9067	13:10:00	14:50:00	2024-09-18	87	576
9068	13:10:00	14:50:00	2024-09-25	87	576
9069	13:10:00	14:50:00	2024-10-02	87	576
8792	11:10:00	12:00:00	2024-10-04	79	546
8793	11:10:00	12:00:00	2024-10-11	79	546
8794	11:10:00	12:00:00	2024-10-18	79	546
8795	11:10:00	12:00:00	2024-10-25	79	546
8796	11:10:00	12:00:00	2024-11-01	79	546
8797	11:10:00	12:00:00	2024-11-08	79	546
8798	11:10:00	12:00:00	2024-11-15	79	546
8799	11:10:00	12:00:00	2024-11-22	79	546
8800	11:10:00	12:00:00	2024-11-29	79	546
8801	11:10:00	12:00:00	2024-12-06	79	546
8875	15:00:00	16:40:00	2024-08-06	87	574
8876	15:00:00	16:40:00	2024-08-13	87	574
8877	15:00:00	16:40:00	2024-08-20	87	574
8878	15:00:00	16:40:00	2024-08-27	87	574
8879	15:00:00	16:40:00	2024-09-03	87	574
8880	15:00:00	16:40:00	2024-09-10	87	574
8881	15:00:00	16:40:00	2024-09-17	87	574
8882	15:00:00	16:40:00	2024-09-24	87	574
8883	15:00:00	16:40:00	2024-10-01	87	574
8884	15:00:00	16:40:00	2024-10-08	87	574
8885	15:00:00	16:40:00	2024-10-15	87	574
8886	15:00:00	16:40:00	2024-10-22	87	574
8887	15:00:00	16:40:00	2024-10-29	87	574
8888	15:00:00	16:40:00	2024-11-05	87	574
8889	15:00:00	16:40:00	2024-11-12	87	574
8890	15:00:00	16:40:00	2024-11-19	87	574
8891	15:00:00	16:40:00	2024-11-26	87	574
8892	15:00:00	16:40:00	2024-12-03	87	574
8893	15:00:00	16:40:00	2024-12-10	87	574
8968	10:10:00	12:00:00	2024-08-09	87	569
8969	10:10:00	12:00:00	2024-08-16	87	569
8970	10:10:00	12:00:00	2024-08-23	87	569
8971	10:10:00	12:00:00	2024-08-30	87	569
8972	10:10:00	12:00:00	2024-09-06	87	569
8973	10:10:00	12:00:00	2024-09-13	87	569
8974	10:10:00	12:00:00	2024-09-20	87	569
8975	10:10:00	12:00:00	2024-09-27	87	569
8976	10:10:00	12:00:00	2024-10-04	87	569
8977	10:10:00	12:00:00	2024-10-11	87	569
8978	10:10:00	12:00:00	2024-10-18	87	569
8979	10:10:00	12:00:00	2024-10-25	87	569
8980	10:10:00	12:00:00	2024-11-01	87	569
8981	10:10:00	12:00:00	2024-11-08	87	569
8982	10:10:00	12:00:00	2024-11-15	87	569
8983	10:10:00	12:00:00	2024-11-22	87	569
8984	10:10:00	12:00:00	2024-11-29	87	569
8985	10:10:00	12:00:00	2024-12-06	87	569
9012	14:00:00	15:50:00	2024-09-30	87	577
9013	14:00:00	15:50:00	2024-10-07	87	577
9014	14:00:00	15:50:00	2024-10-14	87	577
9015	14:00:00	15:50:00	2024-10-21	87	577
9016	14:00:00	15:50:00	2024-10-28	87	577
9017	14:00:00	15:50:00	2024-11-04	87	577
9018	14:00:00	15:50:00	2024-11-11	87	577
9019	14:00:00	15:50:00	2024-11-18	87	577
9020	14:00:00	15:50:00	2024-11-25	87	577
9021	14:00:00	15:50:00	2024-12-02	87	577
9022	14:00:00	15:50:00	2024-12-09	87	577
9023	11:10:00	12:50:00	2024-08-06	87	578
9024	11:10:00	12:50:00	2024-08-13	87	578
9025	11:10:00	12:50:00	2024-08-20	87	578
9026	11:10:00	12:50:00	2024-08-27	87	578
9027	11:10:00	12:50:00	2024-09-03	87	578
9028	11:10:00	12:50:00	2024-09-10	87	578
9029	11:10:00	12:50:00	2024-09-17	87	578
9030	11:10:00	12:50:00	2024-09-24	87	578
9031	11:10:00	12:50:00	2024-10-01	87	578
9032	11:10:00	12:50:00	2024-10-08	87	578
9033	11:10:00	12:50:00	2024-10-15	87	578
9034	11:10:00	12:50:00	2024-10-22	87	578
9035	11:10:00	12:50:00	2024-10-29	87	578
9036	11:10:00	12:50:00	2024-11-05	87	578
9037	11:10:00	12:50:00	2024-11-12	87	578
9038	11:10:00	12:50:00	2024-11-19	87	578
9039	11:10:00	12:50:00	2024-11-26	87	578
9040	11:10:00	12:50:00	2024-12-03	87	578
9041	11:10:00	12:50:00	2024-12-10	87	578
9080	17:40:00	18:30:00	2024-08-05	88	589
9081	17:40:00	18:30:00	2024-08-12	88	589
9082	17:40:00	18:30:00	2024-08-19	88	589
9083	17:40:00	18:30:00	2024-08-26	88	589
9084	17:40:00	18:30:00	2024-09-02	88	589
9085	17:40:00	18:30:00	2024-09-09	88	589
9086	17:40:00	18:30:00	2024-09-16	88	589
9087	17:40:00	18:30:00	2024-09-23	88	589
9088	17:40:00	18:30:00	2024-09-30	88	589
9089	17:40:00	18:30:00	2024-10-07	88	589
9090	17:40:00	18:30:00	2024-10-14	88	589
9091	17:40:00	18:30:00	2024-10-21	88	589
9092	17:40:00	18:30:00	2024-10-28	88	589
9093	17:40:00	18:30:00	2024-11-04	88	589
9094	17:40:00	18:30:00	2024-11-11	88	589
9095	17:40:00	18:30:00	2024-11-18	88	589
9096	17:40:00	18:30:00	2024-11-25	88	589
9097	17:40:00	18:30:00	2024-12-02	88	589
9098	17:40:00	18:30:00	2024-12-09	88	589
9070	13:10:00	14:50:00	2024-10-09	87	576
9071	13:10:00	14:50:00	2024-10-16	87	576
9072	13:10:00	14:50:00	2024-10-23	87	576
9073	13:10:00	14:50:00	2024-10-30	87	576
9074	13:10:00	14:50:00	2024-11-06	87	576
9075	13:10:00	14:50:00	2024-11-13	87	576
9076	13:10:00	14:50:00	2024-11-20	87	576
9077	13:10:00	14:50:00	2024-11-27	87	576
9078	13:10:00	14:50:00	2024-12-04	87	576
9079	13:10:00	14:50:00	2024-12-11	87	576
9117	11:10:00	12:50:00	2024-08-09	88	585
9118	11:10:00	12:50:00	2024-08-16	88	585
9119	11:10:00	12:50:00	2024-08-23	88	585
9120	11:10:00	12:50:00	2024-08-30	88	585
9121	11:10:00	12:50:00	2024-09-06	88	585
9122	11:10:00	12:50:00	2024-09-13	88	585
9123	11:10:00	12:50:00	2024-09-20	88	585
9124	11:10:00	12:50:00	2024-09-27	88	585
9125	11:10:00	12:50:00	2024-10-04	88	585
9126	11:10:00	12:50:00	2024-10-11	88	585
9127	11:10:00	12:50:00	2024-10-18	88	585
9128	11:10:00	12:50:00	2024-10-25	88	585
9129	11:10:00	12:50:00	2024-11-01	88	585
9130	11:10:00	12:50:00	2024-11-08	88	585
9131	11:10:00	12:50:00	2024-11-15	88	585
9132	11:10:00	12:50:00	2024-11-22	88	585
9133	11:10:00	12:50:00	2024-11-29	88	585
9134	11:10:00	12:50:00	2024-12-06	88	585
9135	13:10:00	14:50:00	2024-08-05	88	586
9136	13:10:00	14:50:00	2024-08-12	88	586
9137	13:10:00	14:50:00	2024-08-19	88	586
9138	13:10:00	14:50:00	2024-08-26	88	586
9139	13:10:00	14:50:00	2024-09-02	88	586
9140	13:10:00	14:50:00	2024-09-09	88	586
9141	13:10:00	14:50:00	2024-09-16	88	586
9142	13:10:00	14:50:00	2024-09-23	88	586
9143	13:10:00	14:50:00	2024-09-30	88	586
9144	13:10:00	14:50:00	2024-10-07	88	586
9145	13:10:00	14:50:00	2024-10-14	88	586
9146	13:10:00	14:50:00	2024-10-21	88	586
9147	13:10:00	14:50:00	2024-10-28	88	586
9148	13:10:00	14:50:00	2024-11-04	88	586
9149	13:10:00	14:50:00	2024-11-11	88	586
9150	13:10:00	14:50:00	2024-11-18	88	586
9151	13:10:00	14:50:00	2024-11-25	88	586
9152	13:10:00	14:50:00	2024-12-02	88	586
9153	13:10:00	14:50:00	2024-12-09	88	586
9154	09:20:00	12:00:00	2024-08-05	88	582
9155	09:20:00	12:00:00	2024-08-12	88	582
9156	09:20:00	12:00:00	2024-08-19	88	582
9157	09:20:00	12:00:00	2024-08-26	88	582
9158	09:20:00	12:00:00	2024-09-02	88	582
9159	09:20:00	12:00:00	2024-09-09	88	582
9160	09:20:00	12:00:00	2024-09-16	88	582
9161	09:20:00	12:00:00	2024-09-23	88	582
9162	09:20:00	12:00:00	2024-09-30	88	582
9163	09:20:00	12:00:00	2024-10-07	88	582
9164	09:20:00	12:00:00	2024-10-14	88	582
9165	09:20:00	12:00:00	2024-10-21	88	582
9166	09:20:00	12:00:00	2024-10-28	88	582
9167	09:20:00	12:00:00	2024-11-04	88	582
9168	09:20:00	12:00:00	2024-11-11	88	582
9169	09:20:00	12:00:00	2024-11-18	88	582
9170	09:20:00	12:00:00	2024-11-25	88	582
9171	09:20:00	12:00:00	2024-12-02	88	582
9172	09:20:00	12:00:00	2024-12-09	88	582
9173	07:30:00	09:10:00	2024-08-06	88	579
9174	07:30:00	09:10:00	2024-08-13	88	579
9175	07:30:00	09:10:00	2024-08-20	88	579
9176	07:30:00	09:10:00	2024-08-27	88	579
9177	07:30:00	09:10:00	2024-09-03	88	579
9178	07:30:00	09:10:00	2024-09-10	88	579
9179	07:30:00	09:10:00	2024-09-17	88	579
9180	07:30:00	09:10:00	2024-09-24	88	579
9181	07:30:00	09:10:00	2024-10-01	88	579
9182	07:30:00	09:10:00	2024-10-08	88	579
9183	07:30:00	09:10:00	2024-10-15	88	579
9184	07:30:00	09:10:00	2024-10-22	88	579
9185	07:30:00	09:10:00	2024-10-29	88	579
9186	07:30:00	09:10:00	2024-11-05	88	579
9187	07:30:00	09:10:00	2024-11-12	88	579
9188	07:30:00	09:10:00	2024-11-19	88	579
9189	07:30:00	09:10:00	2024-11-26	88	579
9190	07:30:00	09:10:00	2024-12-03	88	579
9191	07:30:00	09:10:00	2024-12-10	88	579
9192	11:10:00	12:50:00	2024-08-06	88	583
9193	11:10:00	12:50:00	2024-08-13	88	583
9194	11:10:00	12:50:00	2024-08-20	88	583
9195	11:10:00	12:50:00	2024-08-27	88	583
9196	11:10:00	12:50:00	2024-09-03	88	583
9197	11:10:00	12:50:00	2024-09-10	88	583
9198	11:10:00	12:50:00	2024-09-17	88	583
9199	11:10:00	12:50:00	2024-09-24	88	583
9200	11:10:00	12:50:00	2024-10-01	88	583
9201	11:10:00	12:50:00	2024-10-08	88	583
9202	11:10:00	12:50:00	2024-10-15	88	583
9203	11:10:00	12:50:00	2024-10-22	88	583
9204	11:10:00	12:50:00	2024-10-29	88	583
9205	11:10:00	12:50:00	2024-11-05	88	583
9206	11:10:00	12:50:00	2024-11-12	88	583
9207	11:10:00	12:50:00	2024-11-19	88	583
9208	11:10:00	12:50:00	2024-11-26	88	583
9209	11:10:00	12:50:00	2024-12-03	88	583
9210	11:10:00	12:50:00	2024-12-10	88	583
9211	12:00:00	14:00:00	2024-08-07	88	584
9212	12:00:00	14:00:00	2024-08-14	88	584
9213	12:00:00	14:00:00	2024-08-21	88	584
9214	12:00:00	14:00:00	2024-08-28	88	584
9215	12:00:00	14:00:00	2024-09-04	88	584
9216	12:00:00	14:00:00	2024-09-11	88	584
9217	12:00:00	14:00:00	2024-09-18	88	584
9218	12:00:00	14:00:00	2024-09-25	88	584
9219	12:00:00	14:00:00	2024-10-02	88	584
9220	12:00:00	14:00:00	2024-10-09	88	584
9221	12:00:00	14:00:00	2024-10-16	88	584
9222	12:00:00	14:00:00	2024-10-23	88	584
9223	12:00:00	14:00:00	2024-10-30	88	584
9224	12:00:00	14:00:00	2024-11-06	88	584
9225	12:00:00	14:00:00	2024-11-13	88	584
9226	12:00:00	14:00:00	2024-11-20	88	584
9227	12:00:00	14:00:00	2024-11-27	88	584
9228	12:00:00	14:00:00	2024-12-04	88	584
9229	12:00:00	14:00:00	2024-12-11	88	584
9230	08:20:00	12:00:00	2024-08-07	88	581
9231	08:20:00	12:00:00	2024-08-14	88	581
9232	08:20:00	12:00:00	2024-08-21	88	581
9233	08:20:00	12:00:00	2024-08-28	88	581
9234	08:20:00	12:00:00	2024-09-04	88	581
9235	08:20:00	12:00:00	2024-09-11	88	581
9236	08:20:00	12:00:00	2024-09-18	88	581
9237	08:20:00	12:00:00	2024-09-25	88	581
9238	08:20:00	12:00:00	2024-10-02	88	581
9239	08:20:00	12:00:00	2024-10-09	88	581
9240	08:20:00	12:00:00	2024-10-16	88	581
9241	08:20:00	12:00:00	2024-10-23	88	581
9242	08:20:00	12:00:00	2024-10-30	88	581
9243	08:20:00	12:00:00	2024-11-06	88	581
9244	08:20:00	12:00:00	2024-11-13	88	581
9245	08:20:00	12:00:00	2024-11-20	88	581
9246	08:20:00	12:00:00	2024-11-27	88	581
9247	08:20:00	12:00:00	2024-12-04	88	581
9248	08:20:00	12:00:00	2024-12-11	88	581
9399	10:10:00	11:50:00	2024-08-09	89	597
9400	10:10:00	11:50:00	2024-08-16	89	597
9401	10:10:00	11:50:00	2024-08-23	89	597
9402	10:10:00	11:50:00	2024-08-30	89	597
9403	10:10:00	11:50:00	2024-09-06	89	597
9404	10:10:00	11:50:00	2024-09-13	89	597
9405	10:10:00	11:50:00	2024-09-20	89	597
9406	10:10:00	11:50:00	2024-09-27	89	597
9407	10:10:00	11:50:00	2024-10-04	89	597
9408	10:10:00	11:50:00	2024-10-11	89	597
9409	10:10:00	11:50:00	2024-10-18	89	597
9410	10:10:00	11:50:00	2024-10-25	89	597
9411	10:10:00	11:50:00	2024-11-01	89	597
9412	10:10:00	11:50:00	2024-11-08	89	597
9413	10:10:00	11:50:00	2024-11-15	89	597
9414	10:10:00	11:50:00	2024-11-22	89	597
9415	10:10:00	11:50:00	2024-11-29	89	597
9416	10:10:00	11:50:00	2024-12-06	89	597
9473	09:20:00	11:00:00	2024-08-07	90	600
9474	09:20:00	11:00:00	2024-08-14	90	600
9475	09:20:00	11:00:00	2024-08-21	90	600
9476	09:20:00	11:00:00	2024-08-28	90	600
9477	09:20:00	11:00:00	2024-09-04	90	600
9478	09:20:00	11:00:00	2024-09-11	90	600
9479	09:20:00	11:00:00	2024-09-18	90	600
9480	09:20:00	11:00:00	2024-09-25	90	600
9481	09:20:00	11:00:00	2024-10-02	90	600
9482	09:20:00	11:00:00	2024-10-09	90	600
9483	09:20:00	11:00:00	2024-10-16	90	600
9484	09:20:00	11:00:00	2024-10-23	90	600
9485	09:20:00	11:00:00	2024-10-30	90	600
9486	09:20:00	11:00:00	2024-11-06	90	600
9487	09:20:00	11:00:00	2024-11-13	90	600
9488	09:20:00	11:00:00	2024-11-20	90	600
9489	09:20:00	11:00:00	2024-11-27	90	600
9490	09:20:00	11:00:00	2024-12-04	90	600
9491	09:20:00	11:00:00	2024-12-11	90	600
9530	07:30:00	09:10:00	2024-08-05	91	603
9531	07:30:00	09:10:00	2024-08-12	91	603
9532	07:30:00	09:10:00	2024-08-19	91	603
9533	07:30:00	09:10:00	2024-08-26	91	603
9534	07:30:00	09:10:00	2024-09-02	91	603
9535	07:30:00	09:10:00	2024-09-09	91	603
9536	07:30:00	09:10:00	2024-09-16	91	603
9537	07:30:00	09:10:00	2024-09-23	91	603
9538	07:30:00	09:10:00	2024-09-30	91	603
9539	07:30:00	09:10:00	2024-10-07	91	603
9540	07:30:00	09:10:00	2024-10-14	91	603
9541	07:30:00	09:10:00	2024-10-21	91	603
9542	07:30:00	09:10:00	2024-10-28	91	603
9543	07:30:00	09:10:00	2024-11-04	91	603
9544	07:30:00	09:10:00	2024-11-11	91	603
9545	07:30:00	09:10:00	2024-11-18	91	603
9546	07:30:00	09:10:00	2024-11-25	91	603
9547	07:30:00	09:10:00	2024-12-02	91	603
9548	07:30:00	09:10:00	2024-12-09	91	603
9644	10:10:00	12:00:00	2024-08-07	91	609
9645	10:10:00	12:00:00	2024-08-14	91	609
9646	10:10:00	12:00:00	2024-08-21	91	609
9647	10:10:00	12:00:00	2024-08-28	91	609
9648	10:10:00	12:00:00	2024-09-04	91	609
9649	10:10:00	12:00:00	2024-09-11	91	609
9650	10:10:00	12:00:00	2024-09-18	91	609
9651	10:10:00	12:00:00	2024-09-25	91	609
9652	10:10:00	12:00:00	2024-10-02	91	609
9653	10:10:00	12:00:00	2024-10-09	91	609
9654	10:10:00	12:00:00	2024-10-16	91	609
9655	10:10:00	12:00:00	2024-10-23	91	609
9656	10:10:00	12:00:00	2024-10-30	91	609
9657	10:10:00	12:00:00	2024-11-06	91	609
9658	10:10:00	12:00:00	2024-11-13	91	609
9659	10:10:00	12:00:00	2024-11-20	91	609
9660	10:10:00	12:00:00	2024-11-27	91	609
9661	10:10:00	12:00:00	2024-12-04	91	609
9662	10:10:00	12:00:00	2024-12-11	91	609
9720	14:00:00	16:40:00	2024-08-09	91	613
9721	14:00:00	16:40:00	2024-08-16	91	613
9722	14:00:00	16:40:00	2024-08-23	91	613
9723	14:00:00	16:40:00	2024-08-30	91	613
9724	14:00:00	16:40:00	2024-09-06	91	613
9725	14:00:00	16:40:00	2024-09-13	91	613
9726	14:00:00	16:40:00	2024-09-20	91	613
9727	14:00:00	16:40:00	2024-09-27	91	613
9728	14:00:00	16:40:00	2024-10-04	91	613
9729	14:00:00	16:40:00	2024-10-11	91	613
9730	14:00:00	16:40:00	2024-10-18	91	613
9731	14:00:00	16:40:00	2024-10-25	91	613
9732	14:00:00	16:40:00	2024-11-01	91	613
9733	14:00:00	16:40:00	2024-11-08	91	613
9734	14:00:00	16:40:00	2024-11-15	91	613
9735	14:00:00	16:40:00	2024-11-22	91	613
9736	14:00:00	16:40:00	2024-11-29	91	613
9737	14:00:00	16:40:00	2024-12-06	91	613
9795	10:10:00	12:00:00	2024-08-08	87	570
9796	10:10:00	12:00:00	2024-08-15	87	570
9797	10:10:00	12:00:00	2024-08-22	87	570
9798	10:10:00	12:00:00	2024-08-29	87	570
9799	10:10:00	12:00:00	2024-09-05	87	570
9249	13:10:00	14:50:00	2024-08-06	88	587
9250	13:10:00	14:50:00	2024-08-13	88	587
9251	13:10:00	14:50:00	2024-08-20	88	587
9252	13:10:00	14:50:00	2024-08-27	88	587
9253	13:10:00	14:50:00	2024-09-03	88	587
9254	13:10:00	14:50:00	2024-09-10	88	587
9255	13:10:00	14:50:00	2024-09-17	88	587
9256	13:10:00	14:50:00	2024-09-24	88	587
9257	13:10:00	14:50:00	2024-10-01	88	587
9258	13:10:00	14:50:00	2024-10-08	88	587
9259	13:10:00	14:50:00	2024-10-15	88	587
9260	13:10:00	14:50:00	2024-10-22	88	587
9261	13:10:00	14:50:00	2024-10-29	88	587
9262	13:10:00	14:50:00	2024-11-05	88	587
9263	13:10:00	14:50:00	2024-11-12	88	587
9264	13:10:00	14:50:00	2024-11-19	88	587
9265	13:10:00	14:50:00	2024-11-26	88	587
9266	13:10:00	14:50:00	2024-12-03	88	587
9267	13:10:00	14:50:00	2024-12-10	88	587
9362	09:20:00	11:00:00	2024-08-07	89	594
9363	09:20:00	11:00:00	2024-08-14	89	594
9364	09:20:00	11:00:00	2024-08-21	89	594
9365	09:20:00	11:00:00	2024-08-28	89	594
9366	09:20:00	11:00:00	2024-09-04	89	594
9367	09:20:00	11:00:00	2024-09-11	89	594
9368	09:20:00	11:00:00	2024-09-18	89	594
9369	09:20:00	11:00:00	2024-09-25	89	594
9370	09:20:00	11:00:00	2024-10-02	89	594
9371	09:20:00	11:00:00	2024-10-09	89	594
9372	09:20:00	11:00:00	2024-10-16	89	594
9373	09:20:00	11:00:00	2024-10-23	89	594
9374	09:20:00	11:00:00	2024-10-30	89	594
9375	09:20:00	11:00:00	2024-11-06	89	594
9376	09:20:00	11:00:00	2024-11-13	89	594
9377	09:20:00	11:00:00	2024-11-20	89	594
9378	09:20:00	11:00:00	2024-11-27	89	594
9379	09:20:00	11:00:00	2024-12-04	89	594
9380	09:20:00	11:00:00	2024-12-11	89	594
9587	13:10:00	14:50:00	2024-08-07	91	610
9588	13:10:00	14:50:00	2024-08-14	91	610
9589	13:10:00	14:50:00	2024-08-21	91	610
9590	13:10:00	14:50:00	2024-08-28	91	610
9591	13:10:00	14:50:00	2024-09-04	91	610
9592	13:10:00	14:50:00	2024-09-11	91	610
9593	13:10:00	14:50:00	2024-09-18	91	610
9594	13:10:00	14:50:00	2024-09-25	91	610
9595	13:10:00	14:50:00	2024-10-02	91	610
9596	13:10:00	14:50:00	2024-10-09	91	610
9597	13:10:00	14:50:00	2024-10-16	91	610
9598	13:10:00	14:50:00	2024-10-23	91	610
9599	13:10:00	14:50:00	2024-10-30	91	610
9600	13:10:00	14:50:00	2024-11-06	91	610
9601	13:10:00	14:50:00	2024-11-13	91	610
9602	13:10:00	14:50:00	2024-11-20	91	610
9603	13:10:00	14:50:00	2024-11-27	91	610
9604	13:10:00	14:50:00	2024-12-04	91	610
9605	13:10:00	14:50:00	2024-12-11	91	610
9738	07:30:00	09:10:00	2024-08-07	93	616
9739	07:30:00	09:10:00	2024-08-14	93	616
9740	07:30:00	09:10:00	2024-08-21	93	616
9741	07:30:00	09:10:00	2024-08-28	93	616
9742	07:30:00	09:10:00	2024-09-04	93	616
9743	07:30:00	09:10:00	2024-09-11	93	616
9744	07:30:00	09:10:00	2024-09-18	93	616
9745	07:30:00	09:10:00	2024-09-25	93	616
9746	07:30:00	09:10:00	2024-10-02	93	616
9747	07:30:00	09:10:00	2024-10-09	93	616
9748	07:30:00	09:10:00	2024-10-16	93	616
9749	07:30:00	09:10:00	2024-10-23	93	616
9750	07:30:00	09:10:00	2024-10-30	93	616
9751	07:30:00	09:10:00	2024-11-06	93	616
9752	07:30:00	09:10:00	2024-11-13	93	616
9753	07:30:00	09:10:00	2024-11-20	93	616
9754	07:30:00	09:10:00	2024-11-27	93	616
9755	07:30:00	09:10:00	2024-12-04	93	616
9756	07:30:00	09:10:00	2024-12-11	93	616
9814	13:10:00	14:50:00	2024-08-05	47	247
9815	13:10:00	14:50:00	2024-08-12	47	247
9816	13:10:00	14:50:00	2024-08-19	47	247
9817	13:10:00	14:50:00	2024-08-26	47	247
9818	13:10:00	14:50:00	2024-09-02	47	247
9819	13:10:00	14:50:00	2024-09-09	47	247
9820	13:10:00	14:50:00	2024-09-16	47	247
9821	13:10:00	14:50:00	2024-09-23	47	247
9822	13:10:00	14:50:00	2024-09-30	47	247
9823	13:10:00	14:50:00	2024-10-07	47	247
9824	13:10:00	14:50:00	2024-10-14	47	247
9825	13:10:00	14:50:00	2024-10-21	47	247
9826	13:10:00	14:50:00	2024-10-28	47	247
9827	13:10:00	14:50:00	2024-11-04	47	247
9828	13:10:00	14:50:00	2024-11-11	47	247
9829	13:10:00	14:50:00	2024-11-18	47	247
9830	13:10:00	14:50:00	2024-11-25	47	247
9831	13:10:00	14:50:00	2024-12-02	47	247
9832	13:10:00	14:50:00	2024-12-09	47	247
9268	13:10:00	16:40:00	2024-08-08	88	588
9269	13:10:00	16:40:00	2024-08-15	88	588
9270	13:10:00	16:40:00	2024-08-22	88	588
9271	13:10:00	16:40:00	2024-08-29	88	588
9272	13:10:00	16:40:00	2024-09-05	88	588
9273	13:10:00	16:40:00	2024-09-12	88	588
9274	13:10:00	16:40:00	2024-09-19	88	588
9275	13:10:00	16:40:00	2024-09-26	88	588
9276	13:10:00	16:40:00	2024-10-03	88	588
9277	13:10:00	16:40:00	2024-10-10	88	588
9278	13:10:00	16:40:00	2024-10-17	88	588
9279	13:10:00	16:40:00	2024-10-24	88	588
9280	13:10:00	16:40:00	2024-10-31	88	588
9281	13:10:00	16:40:00	2024-11-07	88	588
9282	13:10:00	16:40:00	2024-11-14	88	588
9283	13:10:00	16:40:00	2024-11-21	88	588
9284	13:10:00	16:40:00	2024-11-28	88	588
9285	13:10:00	16:40:00	2024-12-05	88	588
9305	09:20:00	11:00:00	2024-08-05	89	590
9306	09:20:00	11:00:00	2024-08-12	89	590
9307	09:20:00	11:00:00	2024-08-19	89	590
9308	09:20:00	11:00:00	2024-08-26	89	590
9309	09:20:00	11:00:00	2024-09-02	89	590
9310	09:20:00	11:00:00	2024-09-09	89	590
9311	09:20:00	11:00:00	2024-09-16	89	590
9312	09:20:00	11:00:00	2024-09-23	89	590
9313	09:20:00	11:00:00	2024-09-30	89	590
9314	09:20:00	11:00:00	2024-10-07	89	590
9315	09:20:00	11:00:00	2024-10-14	89	590
9316	09:20:00	11:00:00	2024-10-21	89	590
9317	09:20:00	11:00:00	2024-10-28	89	590
9318	09:20:00	11:00:00	2024-11-04	89	590
9319	09:20:00	11:00:00	2024-11-11	89	590
9320	09:20:00	11:00:00	2024-11-18	89	590
9321	09:20:00	11:00:00	2024-11-25	89	590
9322	09:20:00	11:00:00	2024-12-02	89	590
9323	09:20:00	11:00:00	2024-12-09	89	590
9324	11:10:00	12:50:00	2024-08-06	89	591
9325	11:10:00	12:50:00	2024-08-13	89	591
9326	11:10:00	12:50:00	2024-08-20	89	591
9327	11:10:00	12:50:00	2024-08-27	89	591
9328	11:10:00	12:50:00	2024-09-03	89	591
9329	11:10:00	12:50:00	2024-09-10	89	591
9330	11:10:00	12:50:00	2024-09-17	89	591
9331	11:10:00	12:50:00	2024-09-24	89	591
9332	11:10:00	12:50:00	2024-10-01	89	591
9333	11:10:00	12:50:00	2024-10-08	89	591
9334	11:10:00	12:50:00	2024-10-15	89	591
9335	11:10:00	12:50:00	2024-10-22	89	591
9336	11:10:00	12:50:00	2024-10-29	89	591
9337	11:10:00	12:50:00	2024-11-05	89	591
9338	11:10:00	12:50:00	2024-11-12	89	591
9339	11:10:00	12:50:00	2024-11-19	89	591
9340	11:10:00	12:50:00	2024-11-26	89	591
9341	11:10:00	12:50:00	2024-12-03	89	591
9342	11:10:00	12:50:00	2024-12-10	89	591
9381	09:20:00	12:00:00	2024-08-08	89	595
9382	09:20:00	12:00:00	2024-08-15	89	595
9383	09:20:00	12:00:00	2024-08-22	89	595
9384	09:20:00	12:00:00	2024-08-29	89	595
9385	09:20:00	12:00:00	2024-09-05	89	595
9386	09:20:00	12:00:00	2024-09-12	89	595
9387	09:20:00	12:00:00	2024-09-19	89	595
9388	09:20:00	12:00:00	2024-09-26	89	595
9389	09:20:00	12:00:00	2024-10-03	89	595
9390	09:20:00	12:00:00	2024-10-10	89	595
9391	09:20:00	12:00:00	2024-10-17	89	595
9392	09:20:00	12:00:00	2024-10-24	89	595
9393	09:20:00	12:00:00	2024-10-31	89	595
9394	09:20:00	12:00:00	2024-11-07	89	595
9395	09:20:00	12:00:00	2024-11-14	89	595
9396	09:20:00	12:00:00	2024-11-21	89	595
9397	09:20:00	12:00:00	2024-11-28	89	595
9398	09:20:00	12:00:00	2024-12-05	89	595
9606	13:10:00	14:50:00	2024-08-06	91	605
9607	13:10:00	14:50:00	2024-08-13	91	605
9608	13:10:00	14:50:00	2024-08-20	91	605
9609	13:10:00	14:50:00	2024-08-27	91	605
9610	13:10:00	14:50:00	2024-09-03	91	605
9611	13:10:00	14:50:00	2024-09-10	91	605
9612	13:10:00	14:50:00	2024-09-17	91	605
9613	13:10:00	14:50:00	2024-09-24	91	605
9614	13:10:00	14:50:00	2024-10-01	91	605
9615	13:10:00	14:50:00	2024-10-08	91	605
9616	13:10:00	14:50:00	2024-10-15	91	605
9617	13:10:00	14:50:00	2024-10-22	91	605
9618	13:10:00	14:50:00	2024-10-29	91	605
9619	13:10:00	14:50:00	2024-11-05	91	605
9620	13:10:00	14:50:00	2024-11-12	91	605
9621	13:10:00	14:50:00	2024-11-19	91	605
9622	13:10:00	14:50:00	2024-11-26	91	605
9623	13:10:00	14:50:00	2024-12-03	91	605
9624	13:10:00	14:50:00	2024-12-10	91	605
9625	10:10:00	12:00:00	2024-08-08	91	612
9626	10:10:00	12:00:00	2024-08-15	91	612
9627	10:10:00	12:00:00	2024-08-22	91	612
9628	10:10:00	12:00:00	2024-08-29	91	612
9629	10:10:00	12:00:00	2024-09-05	91	612
9630	10:10:00	12:00:00	2024-09-12	91	612
9631	10:10:00	12:00:00	2024-09-19	91	612
9632	10:10:00	12:00:00	2024-09-26	91	612
9633	10:10:00	12:00:00	2024-10-03	91	612
9634	10:10:00	12:00:00	2024-10-10	91	612
9635	10:10:00	12:00:00	2024-10-17	91	612
9636	10:10:00	12:00:00	2024-10-24	91	612
9637	10:10:00	12:00:00	2024-10-31	91	612
9638	10:10:00	12:00:00	2024-11-07	91	612
9639	10:10:00	12:00:00	2024-11-14	91	612
9640	10:10:00	12:00:00	2024-11-21	91	612
9641	10:10:00	12:00:00	2024-11-28	91	612
9642	10:10:00	12:00:00	2024-12-05	91	612
9643	10:10:00	12:00:00	2024-12-12	91	612
9682	15:00:00	16:40:00	2024-08-06	91	606
9683	15:00:00	16:40:00	2024-08-13	91	606
9684	15:00:00	16:40:00	2024-08-20	91	606
9685	15:00:00	16:40:00	2024-08-27	91	606
9686	15:00:00	16:40:00	2024-09-03	91	606
9687	15:00:00	16:40:00	2024-09-10	91	606
9688	15:00:00	16:40:00	2024-09-17	91	606
9689	15:00:00	16:40:00	2024-09-24	91	606
9286	11:10:00	12:50:00	2024-08-05	89	592
9287	11:10:00	12:50:00	2024-08-12	89	592
9288	11:10:00	12:50:00	2024-08-19	89	592
9289	11:10:00	12:50:00	2024-08-26	89	592
9290	11:10:00	12:50:00	2024-09-02	89	592
9291	11:10:00	12:50:00	2024-09-09	89	592
9292	11:10:00	12:50:00	2024-09-16	89	592
9293	11:10:00	12:50:00	2024-09-23	89	592
9294	11:10:00	12:50:00	2024-09-30	89	592
9295	11:10:00	12:50:00	2024-10-07	89	592
9296	11:10:00	12:50:00	2024-10-14	89	592
9297	11:10:00	12:50:00	2024-10-21	89	592
9298	11:10:00	12:50:00	2024-10-28	89	592
9299	11:10:00	12:50:00	2024-11-04	89	592
9300	11:10:00	12:50:00	2024-11-11	89	592
9301	11:10:00	12:50:00	2024-11-18	89	592
9302	11:10:00	12:50:00	2024-11-25	89	592
9303	11:10:00	12:50:00	2024-12-02	89	592
9304	11:10:00	12:50:00	2024-12-09	89	592
9343	09:20:00	11:00:00	2024-08-06	89	593
9344	09:20:00	11:00:00	2024-08-13	89	593
9345	09:20:00	11:00:00	2024-08-20	89	593
9346	09:20:00	11:00:00	2024-08-27	89	593
9347	09:20:00	11:00:00	2024-09-03	89	593
9348	09:20:00	11:00:00	2024-09-10	89	593
9349	09:20:00	11:00:00	2024-09-17	89	593
9350	09:20:00	11:00:00	2024-09-24	89	593
9351	09:20:00	11:00:00	2024-10-01	89	593
9352	09:20:00	11:00:00	2024-10-08	89	593
9353	09:20:00	11:00:00	2024-10-15	89	593
9354	09:20:00	11:00:00	2024-10-22	89	593
9355	09:20:00	11:00:00	2024-10-29	89	593
9356	09:20:00	11:00:00	2024-11-05	89	593
9357	09:20:00	11:00:00	2024-11-12	89	593
9358	09:20:00	11:00:00	2024-11-19	89	593
9359	09:20:00	11:00:00	2024-11-26	89	593
9360	09:20:00	11:00:00	2024-12-03	89	593
9361	09:20:00	11:00:00	2024-12-10	89	593
9435	15:00:00	16:40:00	2024-08-05	89	598
9436	15:00:00	16:40:00	2024-08-12	89	598
9437	15:00:00	16:40:00	2024-08-19	89	598
9438	15:00:00	16:40:00	2024-08-26	89	598
9439	15:00:00	16:40:00	2024-09-02	89	598
9440	15:00:00	16:40:00	2024-09-09	89	598
9441	15:00:00	16:40:00	2024-09-16	89	598
9442	15:00:00	16:40:00	2024-09-23	89	598
9443	15:00:00	16:40:00	2024-09-30	89	598
9444	15:00:00	16:40:00	2024-10-07	89	598
9445	15:00:00	16:40:00	2024-10-14	89	598
9446	15:00:00	16:40:00	2024-10-21	89	598
9447	15:00:00	16:40:00	2024-10-28	89	598
9448	15:00:00	16:40:00	2024-11-04	89	598
9449	15:00:00	16:40:00	2024-11-11	89	598
9450	15:00:00	16:40:00	2024-11-18	89	598
9451	15:00:00	16:40:00	2024-11-25	89	598
9452	15:00:00	16:40:00	2024-12-02	89	598
9453	15:00:00	16:40:00	2024-12-09	89	598
9454	13:10:00	14:50:00	2024-08-07	89	599
9455	13:10:00	14:50:00	2024-08-14	89	599
9456	13:10:00	14:50:00	2024-08-21	89	599
9457	13:10:00	14:50:00	2024-08-28	89	599
9458	13:10:00	14:50:00	2024-09-04	89	599
9459	13:10:00	14:50:00	2024-09-11	89	599
9460	13:10:00	14:50:00	2024-09-18	89	599
9461	13:10:00	14:50:00	2024-09-25	89	599
9462	13:10:00	14:50:00	2024-10-02	89	599
9463	13:10:00	14:50:00	2024-10-09	89	599
9464	13:10:00	14:50:00	2024-10-16	89	599
9465	13:10:00	14:50:00	2024-10-23	89	599
9466	13:10:00	14:50:00	2024-10-30	89	599
9467	13:10:00	14:50:00	2024-11-06	89	599
9468	13:10:00	14:50:00	2024-11-13	89	599
9469	13:10:00	14:50:00	2024-11-20	89	599
9470	13:10:00	14:50:00	2024-11-27	89	599
9471	13:10:00	14:50:00	2024-12-04	89	599
9472	13:10:00	14:50:00	2024-12-11	89	599
9511	14:00:00	17:40:00	2024-08-05	90	602
9512	14:00:00	17:40:00	2024-08-12	90	602
9513	14:00:00	17:40:00	2024-08-19	90	602
9514	14:00:00	17:40:00	2024-08-26	90	602
9515	14:00:00	17:40:00	2024-09-02	90	602
9516	14:00:00	17:40:00	2024-09-09	90	602
9517	14:00:00	17:40:00	2024-09-16	90	602
9518	14:00:00	17:40:00	2024-09-23	90	602
9519	14:00:00	17:40:00	2024-09-30	90	602
9520	14:00:00	17:40:00	2024-10-07	90	602
9521	14:00:00	17:40:00	2024-10-14	90	602
9522	14:00:00	17:40:00	2024-10-21	90	602
9523	14:00:00	17:40:00	2024-10-28	90	602
9524	14:00:00	17:40:00	2024-11-04	90	602
9525	14:00:00	17:40:00	2024-11-11	90	602
9526	14:00:00	17:40:00	2024-11-18	90	602
9527	14:00:00	17:40:00	2024-11-25	90	602
9528	14:00:00	17:40:00	2024-12-02	90	602
9529	14:00:00	17:40:00	2024-12-09	90	602
9568	08:20:00	10:10:00	2024-08-07	91	608
9569	08:20:00	10:10:00	2024-08-14	91	608
9570	08:20:00	10:10:00	2024-08-21	91	608
9571	08:20:00	10:10:00	2024-08-28	91	608
9572	08:20:00	10:10:00	2024-09-04	91	608
9573	08:20:00	10:10:00	2024-09-11	91	608
9574	08:20:00	10:10:00	2024-09-18	91	608
9575	08:20:00	10:10:00	2024-09-25	91	608
9576	08:20:00	10:10:00	2024-10-02	91	608
9577	08:20:00	10:10:00	2024-10-09	91	608
9578	08:20:00	10:10:00	2024-10-16	91	608
9579	08:20:00	10:10:00	2024-10-23	91	608
9580	08:20:00	10:10:00	2024-10-30	91	608
9581	08:20:00	10:10:00	2024-11-06	91	608
9582	08:20:00	10:10:00	2024-11-13	91	608
9583	08:20:00	10:10:00	2024-11-20	91	608
9584	08:20:00	10:10:00	2024-11-27	91	608
9585	08:20:00	10:10:00	2024-12-04	91	608
9586	08:20:00	10:10:00	2024-12-11	91	608
9757	10:00:00	12:00:00	2024-08-06	93	614
9758	10:00:00	12:00:00	2024-08-13	93	614
9759	10:00:00	12:00:00	2024-08-20	93	614
9760	10:00:00	12:00:00	2024-08-27	93	614
9761	10:00:00	12:00:00	2024-09-03	93	614
9762	10:00:00	12:00:00	2024-09-10	93	614
9417	07:30:00	11:00:00	2024-08-09	89	596
9418	07:30:00	11:00:00	2024-08-16	89	596
9419	07:30:00	11:00:00	2024-08-23	89	596
9420	07:30:00	11:00:00	2024-08-30	89	596
9421	07:30:00	11:00:00	2024-09-06	89	596
9422	07:30:00	11:00:00	2024-09-13	89	596
9423	07:30:00	11:00:00	2024-09-20	89	596
9424	07:30:00	11:00:00	2024-09-27	89	596
9425	07:30:00	11:00:00	2024-10-04	89	596
9426	07:30:00	11:00:00	2024-10-11	89	596
9427	07:30:00	11:00:00	2024-10-18	89	596
9428	07:30:00	11:00:00	2024-10-25	89	596
9429	07:30:00	11:00:00	2024-11-01	89	596
9430	07:30:00	11:00:00	2024-11-08	89	596
9431	07:30:00	11:00:00	2024-11-15	89	596
9432	07:30:00	11:00:00	2024-11-22	89	596
9433	07:30:00	11:00:00	2024-11-29	89	596
9434	07:30:00	11:00:00	2024-12-06	89	596
9492	13:10:00	14:50:00	2024-08-07	90	601
9493	13:10:00	14:50:00	2024-08-14	90	601
9494	13:10:00	14:50:00	2024-08-21	90	601
9495	13:10:00	14:50:00	2024-08-28	90	601
9496	13:10:00	14:50:00	2024-09-04	90	601
9497	13:10:00	14:50:00	2024-09-11	90	601
9498	13:10:00	14:50:00	2024-09-18	90	601
9499	13:10:00	14:50:00	2024-09-25	90	601
9500	13:10:00	14:50:00	2024-10-02	90	601
9501	13:10:00	14:50:00	2024-10-09	90	601
9502	13:10:00	14:50:00	2024-10-16	90	601
9503	13:10:00	14:50:00	2024-10-23	90	601
9504	13:10:00	14:50:00	2024-10-30	90	601
9505	13:10:00	14:50:00	2024-11-06	90	601
9506	13:10:00	14:50:00	2024-11-13	90	601
9507	13:10:00	14:50:00	2024-11-20	90	601
9508	13:10:00	14:50:00	2024-11-27	90	601
9509	13:10:00	14:50:00	2024-12-04	90	601
9510	13:10:00	14:50:00	2024-12-11	90	601
9549	15:00:00	16:40:00	2024-08-07	91	611
9550	15:00:00	16:40:00	2024-08-14	91	611
9551	15:00:00	16:40:00	2024-08-21	91	611
9552	15:00:00	16:40:00	2024-08-28	91	611
9553	15:00:00	16:40:00	2024-09-04	91	611
9554	15:00:00	16:40:00	2024-09-11	91	611
9555	15:00:00	16:40:00	2024-09-18	91	611
9556	15:00:00	16:40:00	2024-09-25	91	611
9557	15:00:00	16:40:00	2024-10-02	91	611
9558	15:00:00	16:40:00	2024-10-09	91	611
9559	15:00:00	16:40:00	2024-10-16	91	611
9560	15:00:00	16:40:00	2024-10-23	91	611
9561	15:00:00	16:40:00	2024-10-30	91	611
9562	15:00:00	16:40:00	2024-11-06	91	611
9563	15:00:00	16:40:00	2024-11-13	91	611
9564	15:00:00	16:40:00	2024-11-20	91	611
9565	15:00:00	16:40:00	2024-11-27	91	611
9566	15:00:00	16:40:00	2024-12-04	91	611
9567	15:00:00	16:40:00	2024-12-11	91	611
9663	13:10:00	15:50:00	2024-08-05	91	604
9664	13:10:00	15:50:00	2024-08-12	91	604
9665	13:10:00	15:50:00	2024-08-19	91	604
9666	13:10:00	15:50:00	2024-08-26	91	604
9667	13:10:00	15:50:00	2024-09-02	91	604
9668	13:10:00	15:50:00	2024-09-09	91	604
9669	13:10:00	15:50:00	2024-09-16	91	604
9670	13:10:00	15:50:00	2024-09-23	91	604
9671	13:10:00	15:50:00	2024-09-30	91	604
9672	13:10:00	15:50:00	2024-10-07	91	604
9673	13:10:00	15:50:00	2024-10-14	91	604
9674	13:10:00	15:50:00	2024-10-21	91	604
9675	13:10:00	15:50:00	2024-10-28	91	604
9676	13:10:00	15:50:00	2024-11-04	91	604
9677	13:10:00	15:50:00	2024-11-11	91	604
9678	13:10:00	15:50:00	2024-11-18	91	604
9679	13:10:00	15:50:00	2024-11-25	91	604
9680	13:10:00	15:50:00	2024-12-02	91	604
9681	13:10:00	15:50:00	2024-12-09	91	604
9690	15:00:00	16:40:00	2024-10-01	91	606
9691	15:00:00	16:40:00	2024-10-08	91	606
9692	15:00:00	16:40:00	2024-10-15	91	606
9693	15:00:00	16:40:00	2024-10-22	91	606
9694	15:00:00	16:40:00	2024-10-29	91	606
9695	15:00:00	16:40:00	2024-11-05	91	606
9696	15:00:00	16:40:00	2024-11-12	91	606
9697	15:00:00	16:40:00	2024-11-19	91	606
9698	15:00:00	16:40:00	2024-11-26	91	606
9699	15:00:00	16:40:00	2024-12-03	91	606
9700	15:00:00	16:40:00	2024-12-10	91	606
9701	13:10:00	14:50:00	2024-08-08	91	607
9702	13:10:00	14:50:00	2024-08-15	91	607
9703	13:10:00	14:50:00	2024-08-22	91	607
9704	13:10:00	14:50:00	2024-08-29	91	607
9705	13:10:00	14:50:00	2024-09-05	91	607
9706	13:10:00	14:50:00	2024-09-12	91	607
9707	13:10:00	14:50:00	2024-09-19	91	607
9708	13:10:00	14:50:00	2024-09-26	91	607
9709	13:10:00	14:50:00	2024-10-03	91	607
9710	13:10:00	14:50:00	2024-10-10	91	607
9711	13:10:00	14:50:00	2024-10-17	91	607
9712	13:10:00	14:50:00	2024-10-24	91	607
9713	13:10:00	14:50:00	2024-10-31	91	607
9714	13:10:00	14:50:00	2024-11-07	91	607
9715	13:10:00	14:50:00	2024-11-14	91	607
9716	13:10:00	14:50:00	2024-11-21	91	607
9717	13:10:00	14:50:00	2024-11-28	91	607
9718	13:10:00	14:50:00	2024-12-05	91	607
9719	13:10:00	14:50:00	2024-12-12	91	607
9763	10:00:00	12:00:00	2024-09-17	93	614
9764	10:00:00	12:00:00	2024-09-24	93	614
9765	10:00:00	12:00:00	2024-10-01	93	614
9766	10:00:00	12:00:00	2024-10-08	93	614
9767	10:00:00	12:00:00	2024-10-15	93	614
9768	10:00:00	12:00:00	2024-10-22	93	614
9769	10:00:00	12:00:00	2024-10-29	93	614
9770	10:00:00	12:00:00	2024-11-05	93	614
9771	10:00:00	12:00:00	2024-11-12	93	614
9772	10:00:00	12:00:00	2024-11-19	93	614
9773	10:00:00	12:00:00	2024-11-26	93	614
9774	10:00:00	12:00:00	2024-12-03	93	614
9775	10:00:00	12:00:00	2024-12-10	93	614
9776	10:00:00	12:00:00	2024-08-07	93	615
9777	10:00:00	12:00:00	2024-08-14	93	615
9778	10:00:00	12:00:00	2024-08-21	93	615
9779	10:00:00	12:00:00	2024-08-28	93	615
9780	10:00:00	12:00:00	2024-09-04	93	615
9781	10:00:00	12:00:00	2024-09-11	93	615
9782	10:00:00	12:00:00	2024-09-18	93	615
9783	10:00:00	12:00:00	2024-09-25	93	615
9784	10:00:00	12:00:00	2024-10-02	93	615
9785	10:00:00	12:00:00	2024-10-09	93	615
9786	10:00:00	12:00:00	2024-10-16	93	615
9787	10:00:00	12:00:00	2024-10-23	93	615
9788	10:00:00	12:00:00	2024-10-30	93	615
9789	10:00:00	12:00:00	2024-11-06	93	615
9790	10:00:00	12:00:00	2024-11-13	93	615
9791	10:00:00	12:00:00	2024-11-20	93	615
9792	10:00:00	12:00:00	2024-11-27	93	615
9793	10:00:00	12:00:00	2024-12-04	93	615
9794	10:00:00	12:00:00	2024-12-11	93	615
9833	09:20:00	11:00:00	2024-08-05	53	644
9834	09:20:00	11:00:00	2024-08-12	53	644
9835	09:20:00	11:00:00	2024-08-19	53	644
9836	09:20:00	11:00:00	2024-08-26	53	644
9837	09:20:00	11:00:00	2024-09-02	53	644
9838	09:20:00	11:00:00	2024-09-09	53	644
9839	09:20:00	11:00:00	2024-09-16	53	644
9840	09:20:00	11:00:00	2024-09-23	53	644
9841	09:20:00	11:00:00	2024-09-30	53	644
9842	09:20:00	11:00:00	2024-10-07	53	644
9843	09:20:00	11:00:00	2024-10-14	53	644
9844	09:20:00	11:00:00	2024-10-21	53	644
9845	09:20:00	11:00:00	2024-10-28	53	644
9846	09:20:00	11:00:00	2024-11-04	53	644
9847	09:20:00	11:00:00	2024-11-11	53	644
9848	09:20:00	11:00:00	2024-11-18	53	644
9849	09:20:00	11:00:00	2024-11-25	53	644
9850	09:20:00	11:00:00	2024-12-02	53	644
9851	09:20:00	11:00:00	2024-12-09	53	644
9800	10:10:00	12:00:00	2024-09-12	87	570
9801	10:10:00	12:00:00	2024-09-19	87	570
9802	10:10:00	12:00:00	2024-09-26	87	570
9803	10:10:00	12:00:00	2024-10-03	87	570
9804	10:10:00	12:00:00	2024-10-10	87	570
9805	10:10:00	12:00:00	2024-10-17	87	570
9806	10:10:00	12:00:00	2024-10-24	87	570
9807	10:10:00	12:00:00	2024-10-31	87	570
9808	10:10:00	12:00:00	2024-11-07	87	570
9809	10:10:00	12:00:00	2024-11-14	87	570
9810	10:10:00	12:00:00	2024-11-21	87	570
9811	10:10:00	12:00:00	2024-11-28	87	570
9812	10:10:00	12:00:00	2024-12-05	87	570
9813	10:10:00	12:00:00	2024-12-12	87	570
9852	08:00:00	12:00:00	2024-08-05	45	617
9853	08:00:00	12:00:00	2024-08-12	45	617
9854	08:00:00	12:00:00	2024-08-19	45	617
9855	08:00:00	12:00:00	2024-08-26	45	617
9856	08:00:00	12:00:00	2024-09-02	45	617
9857	08:00:00	12:00:00	2024-09-09	45	617
9858	08:00:00	12:00:00	2024-09-16	45	617
9859	08:00:00	12:00:00	2024-09-23	45	617
9860	08:00:00	12:00:00	2024-09-30	45	617
9861	08:00:00	12:00:00	2024-10-07	45	617
9862	08:00:00	12:00:00	2024-10-14	45	617
9863	08:00:00	12:00:00	2024-10-21	45	617
9864	08:00:00	12:00:00	2024-10-28	45	617
9865	08:00:00	12:00:00	2024-11-04	45	617
9866	08:00:00	12:00:00	2024-11-11	45	617
9867	08:00:00	12:00:00	2024-11-18	45	617
9868	08:00:00	12:00:00	2024-11-25	45	617
9869	08:00:00	12:00:00	2024-12-02	45	617
9870	08:00:00	12:00:00	2024-12-09	45	617
\.


--
-- TOC entry 3226 (class 0 OID 25243)
-- Dependencies: 230
-- Data for Name: reservation; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.reservation (id, name, type, description, updated_at, classroom_id, created_by_id) FROM stdin;
\.


--
-- TOC entry 3228 (class 0 OID 25307)
-- Dependencies: 232
-- Data for Name: schedule; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.schedule (id, start_date, end_date, start_time, end_time, week_day, allocated, recurrence, month_week, all_day, class_id, classroom_id, reservation_id) FROM stdin;
29	2024-08-05	2024-12-12	07:30:00	11:00:00	MONDAY	f	WEEKLY	\N	f	28	\N	\N
30	2024-08-05	2024-12-12	07:30:00	11:00:00	MONDAY	f	WEEKLY	\N	f	29	\N	\N
31	2024-08-05	2024-12-12	07:30:00	11:00:00	MONDAY	f	WEEKLY	\N	f	30	\N	\N
32	2024-08-05	2024-12-12	07:30:00	11:00:00	MONDAY	f	WEEKLY	\N	f	31	\N	\N
579	2024-08-05	2024-12-11	07:30:00	09:10:00	TUESDAY	t	WEEKLY	\N	f	396	88	\N
39	2024-08-05	2024-12-12	07:30:00	11:00:00	WEDNESDAY	f	WEEKLY	\N	f	37	\N	\N
40	2024-08-05	2024-12-12	07:30:00	11:00:00	WEDNESDAY	f	WEEKLY	\N	f	38	\N	\N
43	2024-08-05	2024-12-12	15:00:00	16:40:00	TUESDAY	f	WEEKLY	\N	f	41	\N	\N
44	2024-08-05	2024-12-12	16:50:00	18:30:00	TUESDAY	f	WEEKLY	\N	f	42	\N	\N
3	2024-08-05	2024-12-12	07:30:00	11:00:00	TUESDAY	t	WEEKLY	\N	f	2	66	\N
4	2024-08-05	2024-12-12	07:30:00	11:00:00	TUESDAY	t	WEEKLY	\N	f	3	66	\N
5	2024-08-05	2024-12-12	13:10:00	16:40:00	FRIDAY	t	WEEKLY	\N	f	4	66	\N
6	2024-08-05	2024-12-12	13:10:00	16:40:00	FRIDAY	t	WEEKLY	\N	f	5	66	\N
7	2024-08-05	2024-12-12	13:10:00	14:50:00	MONDAY	t	WEEKLY	\N	f	6	65	\N
8	2024-08-05	2024-12-12	13:10:00	14:50:00	WEDNESDAY	t	WEEKLY	\N	f	7	35	\N
9	2024-08-05	2024-12-12	09:20:00	11:00:00	THURSDAY	t	WEEKLY	\N	f	8	38	\N
11	2024-05-06	2024-08-16	13:10:00	16:40:00	WEDNESDAY	t	WEEKLY	\N	f	10	67	\N
12	2024-05-06	2024-08-16	13:10:00	16:40:00	FRIDAY	t	WEEKLY	\N	f	11	67	\N
13	2024-05-06	2024-08-16	13:10:00	16:40:00	FRIDAY	t	WEEKLY	\N	f	12	67	\N
10	2024-05-06	2024-08-16	13:10:00	16:40:00	WEDNESDAY	t	WEEKLY	\N	f	9	67	\N
15	2024-08-05	2024-12-12	08:20:00	11:00:00	FRIDAY	t	WEEKLY	\N	f	14	27	\N
16	2024-08-05	2024-12-12	07:30:00	11:00:00	THURSDAY	t	WEEKLY	\N	f	15	66	\N
17	2024-08-05	2024-12-12	07:30:00	11:00:00	THURSDAY	t	WEEKLY	\N	f	16	66	\N
18	2024-08-05	2024-12-12	14:00:00	17:30:00	THURSDAY	t	WEEKLY	\N	f	17	66	\N
19	2024-08-05	2024-12-12	14:00:00	17:30:00	THURSDAY	t	WEEKLY	\N	f	18	66	\N
20	2024-08-05	2024-12-12	07:30:00	09:10:00	WEDNESDAY	t	WEEKLY	\N	f	19	38	\N
25	2024-08-05	2024-12-12	15:00:00	16:40:00	MONDAY	t	WEEKLY	\N	f	24	65	\N
21	2024-08-05	2024-12-12	07:30:00	11:00:00	WEDNESDAY	t	WEEKLY	\N	f	20	66	\N
22	2024-08-05	2024-12-12	07:30:00	11:00:00	WEDNESDAY	t	WEEKLY	\N	f	21	66	\N
23	2024-08-05	2024-12-12	07:30:00	11:00:00	FRIDAY	t	WEEKLY	\N	f	22	66	\N
24	2024-08-05	2024-12-12	07:30:00	11:00:00	FRIDAY	t	WEEKLY	\N	f	23	66	\N
26	2024-08-05	2024-12-12	07:30:00	11:00:00	THURSDAY	t	WEEKLY	\N	f	25	27	\N
27	2024-08-05	2024-12-12	07:30:00	11:00:00	THURSDAY	t	WEEKLY	\N	f	26	27	\N
28	2024-08-05	2024-12-12	13:10:00	16:40:00	FRIDAY	t	WEEKLY	\N	f	27	27	\N
33	2024-08-05	2024-12-12	15:00:00	16:40:00	MONDAY	t	WEEKLY	\N	f	32	35	\N
34	2024-08-05	2024-12-12	13:10:00	14:50:00	WEDNESDAY	t	WEEKLY	\N	f	33	27	\N
36	2024-08-05	2024-12-12	07:30:00	11:00:00	WEDNESDAY	t	WEEKLY	\N	f	34	67	\N
37	2024-08-05	2024-12-12	07:30:00	11:00:00	WEDNESDAY	t	WEEKLY	\N	f	35	67	\N
38	2024-08-05	2024-12-12	16:50:00	18:30:00	WEDNESDAY	t	WEEKLY	\N	f	36	67	\N
41	2024-08-05	2024-12-12	16:50:00	18:30:00	MONDAY	t	WEEKLY	\N	f	39	27	\N
46	2024-08-05	2024-12-12	09:20:00	11:10:00	SATURDAY	t	WEEKLY	\N	f	44	68	\N
45	2024-08-05	2024-12-12	13:10:00	14:50:00	MONDAY	t	WEEKLY	\N	f	43	35	\N
42	2024-08-05	2024-12-12	13:10:00	14:50:00	TUESDAY	f	WEEKLY	\N	f	40	\N	\N
47	2024-08-05	2024-12-12	07:30:00	09:10:00	SATURDAY	t	WEEKLY	\N	f	45	68	\N
48	2024-08-05	2024-12-12	07:30:00	09:10:00	SATURDAY	t	WEEKLY	\N	f	46	68	\N
49	2024-08-05	2024-12-12	07:30:00	09:10:00	SATURDAY	t	WEEKLY	\N	f	47	68	\N
50	2024-08-05	2024-12-12	07:30:00	09:10:00	SATURDAY	t	WEEKLY	\N	f	48	68	\N
51	2024-08-05	2024-12-12	07:30:00	09:10:00	SATURDAY	t	WEEKLY	\N	f	49	68	\N
52	2024-08-05	2024-12-12	07:30:00	11:00:00	TUESDAY	t	WEEKLY	\N	f	50	27	\N
53	2024-08-05	2024-12-12	16:50:00	18:30:00	MONDAY	t	WEEKLY	\N	f	51	35	\N
55	2024-08-05	2024-12-12	11:20:00	12:10:00	SATURDAY	t	WEEKLY	\N	f	52	68	\N
56	2024-08-05	2024-12-12	09:20:00	11:00:00	MONDAY	t	WEEKLY	\N	f	53	30	\N
57	2024-08-05	2024-12-12	09:20:00	11:00:00	THURSDAY	t	WEEKLY	\N	f	53	32	\N
58	2024-08-05	2024-12-12	09:20:00	11:00:00	MONDAY	t	WEEKLY	\N	f	54	31	\N
59	2024-08-05	2024-12-12	09:20:00	11:00:00	THURSDAY	t	WEEKLY	\N	f	54	31	\N
60	2024-08-05	2024-12-12	09:20:00	11:00:00	MONDAY	t	WEEKLY	\N	f	55	33	\N
61	2024-08-05	2024-12-12	09:20:00	11:00:00	THURSDAY	t	WEEKLY	\N	f	55	33	\N
62	2024-08-05	2024-12-12	07:30:00	09:10:00	TUESDAY	t	WEEKLY	\N	f	56	30	\N
63	2024-08-05	2024-12-12	07:30:00	09:10:00	FRIDAY	t	WEEKLY	\N	f	56	38	\N
64	2024-08-05	2024-12-12	07:30:00	09:10:00	TUESDAY	t	WEEKLY	\N	f	57	31	\N
65	2024-08-05	2024-12-12	07:30:00	09:10:00	FRIDAY	t	WEEKLY	\N	f	57	31	\N
66	2024-08-05	2024-12-12	07:30:00	09:10:00	TUESDAY	t	WEEKLY	\N	f	58	33	\N
67	2024-08-05	2024-12-12	07:30:00	09:10:00	FRIDAY	t	WEEKLY	\N	f	58	33	\N
68	2024-08-05	2024-12-12	11:10:00	12:50:00	TUESDAY	t	WEEKLY	\N	f	59	30	\N
69	2024-08-05	2024-12-12	11:10:00	12:50:00	THURSDAY	t	WEEKLY	\N	f	59	30	\N
70	2024-08-05	2024-12-12	11:10:00	12:50:00	TUESDAY	t	WEEKLY	\N	f	60	31	\N
71	2024-08-05	2024-12-12	11:10:00	12:50:00	THURSDAY	t	WEEKLY	\N	f	60	31	\N
72	2024-08-05	2024-12-12	11:10:00	12:50:00	TUESDAY	t	WEEKLY	\N	f	61	33	\N
73	2024-08-05	2024-12-12	11:10:00	12:50:00	THURSDAY	t	WEEKLY	\N	f	61	33	\N
74	2024-08-05	2024-12-12	11:10:00	12:50:00	MONDAY	t	WEEKLY	\N	f	62	30	\N
75	2024-08-05	2024-12-12	11:10:00	12:50:00	MONDAY	t	WEEKLY	\N	f	63	31	\N
76	2024-08-05	2024-12-12	11:10:00	12:50:00	MONDAY	t	WEEKLY	\N	f	64	33	\N
77	2024-08-05	2024-12-12	07:30:00	11:00:00	WEDNESDAY	t	WEEKLY	\N	f	65	72	\N
78	2024-08-05	2024-12-12	14:00:00	15:40:00	MONDAY	t	WEEKLY	\N	f	66	21	\N
80	2024-08-05	2024-12-12	15:50:00	17:30:00	TUESDAY	t	WEEKLY	\N	f	67	21	\N
81	2024-08-05	2024-12-12	15:50:00	17:30:00	THURSDAY	t	WEEKLY	\N	f	67	21	\N
82	2024-08-05	2024-12-12	14:00:00	15:40:00	TUESDAY	t	WEEKLY	\N	f	68	21	\N
83	2024-08-05	2024-12-12	15:50:00	17:30:00	WEDNESDAY	t	WEEKLY	\N	f	68	21	\N
84	2024-08-05	2024-12-12	09:20:00	10:10:00	SATURDAY	t	WEEKLY	\N	f	69	68	\N
85	2024-08-05	2024-12-12	10:20:00	11:10:00	SATURDAY	t	WEEKLY	\N	f	70	68	\N
87	2024-08-05	2024-12-12	10:20:00	11:10:00	SATURDAY	t	WEEKLY	\N	f	72	68	\N
86	2024-08-05	2024-12-12	10:20:00	11:10:00	SATURDAY	t	WEEKLY	\N	f	71	68	\N
88	2024-08-05	2024-12-12	08:30:00	12:00:00	FRIDAY	t	WEEKLY	\N	f	73	72	\N
14	2024-05-06	2024-08-16	09:20:00	11:00:00	THURSDAY	t	WEEKLY	\N	f	13	30	\N
93	2024-08-05	2024-12-12	15:00:00	17:40:00	MONDAY	f	WEEKLY	\N	f	77	\N	\N
94	2024-08-05	2024-12-12	15:00:00	17:40:00	TUESDAY	f	WEEKLY	\N	f	78	\N	\N
95	2024-08-05	2024-12-12	15:00:00	17:40:00	WEDNESDAY	f	WEEKLY	\N	f	79	\N	\N
96	2024-08-05	2024-12-12	15:00:00	17:40:00	THURSDAY	f	WEEKLY	\N	f	80	\N	\N
97	2024-08-05	2024-12-12	15:00:00	17:40:00	FRIDAY	f	WEEKLY	\N	f	81	\N	\N
108	2024-08-05	2024-12-12	11:10:00	12:50:00	TUESDAY	f	WEEKLY	\N	f	87	\N	\N
109	2024-08-05	2024-12-12	11:10:00	12:50:00	THURSDAY	f	WEEKLY	\N	f	87	\N	\N
110	2024-08-05	2024-12-12	09:20:00	11:00:00	WEDNESDAY	f	WEEKLY	\N	f	88	\N	\N
111	2024-08-05	2024-12-12	09:20:00	11:00:00	FRIDAY	f	WEEKLY	\N	f	88	\N	\N
114	2024-08-05	2024-12-12	14:00:00	17:40:00	MONDAY	f	WEEKLY	\N	f	90	\N	\N
115	2024-08-05	2024-12-12	14:00:00	17:50:00	WEDNESDAY	f	WEEKLY	\N	f	91	\N	\N
116	2024-08-05	2024-12-12	11:00:00	12:00:00	SATURDAY	f	WEEKLY	\N	f	92	\N	\N
117	2024-08-05	2024-12-12	07:30:00	09:20:00	SATURDAY	f	WEEKLY	\N	f	93	\N	\N
118	2024-08-05	2024-12-12	07:30:00	09:20:00	SATURDAY	f	WEEKLY	\N	f	94	\N	\N
119	2024-08-05	2024-12-12	07:30:00	09:20:00	SATURDAY	f	WEEKLY	\N	f	95	\N	\N
120	2024-08-05	2024-12-12	09:20:00	11:00:00	SATURDAY	f	WEEKLY	\N	f	96	\N	\N
121	2024-08-05	2024-12-12	09:20:00	11:00:00	SATURDAY	f	WEEKLY	\N	f	97	\N	\N
122	2024-08-05	2024-12-12	09:20:00	11:00:00	SATURDAY	f	WEEKLY	\N	f	98	\N	\N
124	2024-08-05	2024-12-12	14:00:00	17:40:00	FRIDAY	f	WEEKLY	\N	f	100	\N	\N
581	2024-08-05	2024-12-11	08:20:00	12:00:00	WEDNESDAY	t	WEEKLY	\N	f	398	88	\N
143	2024-08-05	2024-12-12	09:20:00	11:00:00	WEDNESDAY	f	WEEKLY	\N	f	110	\N	\N
170	2024-08-05	2024-12-12	13:10:00	15:50:00	TUESDAY	f	WEEKLY	\N	f	128	\N	\N
171	2024-08-05	2024-12-12	13:10:00	15:50:00	TUESDAY	f	WEEKLY	\N	f	129	\N	\N
172	2024-08-05	2024-12-12	13:10:00	15:50:00	WEDNESDAY	f	WEEKLY	\N	f	130	\N	\N
173	2024-08-05	2024-12-12	13:10:00	15:50:00	WEDNESDAY	f	WEEKLY	\N	f	131	\N	\N
174	2024-08-05	2024-12-12	08:20:00	11:00:00	THURSDAY	f	WEEKLY	\N	f	132	\N	\N
175	2024-08-05	2024-12-12	08:20:00	11:00:00	THURSDAY	f	WEEKLY	\N	f	133	\N	\N
176	2024-08-05	2024-12-12	14:00:00	17:40:00	WEDNESDAY	f	WEEKLY	\N	f	134	\N	\N
90	2024-05-06	2024-08-16	08:20:00	10:00:00	TUESDAY	t	WEEKLY	\N	f	75	23	\N
92	2024-08-05	2024-12-12	16:50:00	18:30:00	TUESDAY	t	WEEKLY	\N	f	76	22	\N
98	2024-08-05	2024-12-12	11:10:00	12:50:00	WEDNESDAY	t	WEEKLY	\N	f	82	38	\N
99	2024-08-05	2024-12-12	09:20:00	11:00:00	FRIDAY	t	WEEKLY	\N	f	82	38	\N
100	2024-08-05	2024-12-12	11:10:00	12:50:00	WEDNESDAY	t	WEEKLY	\N	f	83	32	\N
101	2024-08-05	2024-12-12	09:20:00	11:00:00	FRIDAY	t	WEEKLY	\N	f	83	32	\N
102	2024-08-05	2024-12-12	11:10:00	12:50:00	WEDNESDAY	t	WEEKLY	\N	f	84	33	\N
103	2024-08-05	2024-12-12	09:20:00	11:00:00	FRIDAY	t	WEEKLY	\N	f	84	33	\N
104	2024-08-05	2024-12-12	07:30:00	09:10:00	WEDNESDAY	t	WEEKLY	\N	f	85	22	\N
105	2024-08-05	2024-12-12	07:30:00	09:10:00	FRIDAY	t	WEEKLY	\N	f	85	22	\N
106	2024-08-05	2024-12-12	11:10:00	12:50:00	WEDNESDAY	t	WEEKLY	\N	f	86	22	\N
107	2024-08-05	2024-12-12	11:10:00	12:50:00	FRIDAY	t	WEEKLY	\N	f	86	22	\N
112	2024-08-05	2024-12-12	09:20:00	11:00:00	TUESDAY	t	WEEKLY	\N	f	89	22	\N
113	2024-08-05	2024-12-12	09:20:00	11:00:00	THURSDAY	t	WEEKLY	\N	f	89	22	\N
123	2024-08-05	2024-12-12	07:30:00	11:00:00	WEDNESDAY	t	WEEKLY	\N	f	99	26	\N
125	2024-08-05	2024-12-12	09:20:00	12:50:00	TUESDAY	t	WEEKLY	\N	f	101	21	\N
126	2024-08-05	2024-12-12	09:20:00	11:00:00	MONDAY	t	WEEKLY	\N	f	102	38	\N
127	2024-08-05	2024-12-12	07:30:00	09:10:00	FRIDAY	t	WEEKLY	\N	f	102	30	\N
129	2024-08-05	2024-12-12	07:30:00	09:10:00	MONDAY	t	WEEKLY	\N	f	103	24	\N
130	2024-08-05	2024-12-12	07:30:00	09:10:00	WEDNESDAY	t	WEEKLY	\N	f	103	24	\N
131	2024-08-05	2024-12-12	15:00:00	16:40:00	MONDAY	t	WEEKLY	\N	f	104	30	\N
132	2024-08-05	2024-12-12	13:10:00	14:50:00	WEDNESDAY	t	WEEKLY	\N	f	104	30	\N
133	2024-08-05	2024-12-12	15:00:00	16:40:00	MONDAY	t	WEEKLY	\N	f	105	33	\N
134	2024-08-05	2024-12-12	13:10:00	14:50:00	WEDNESDAY	t	WEEKLY	\N	f	105	33	\N
135	2024-08-05	2024-12-12	15:00:00	16:40:00	MONDAY	t	WEEKLY	\N	f	106	31	\N
136	2024-08-05	2024-12-12	13:10:00	14:50:00	WEDNESDAY	t	WEEKLY	\N	f	106	31	\N
137	2024-08-05	2024-12-12	15:00:00	16:40:00	MONDAY	t	WEEKLY	\N	f	107	24	\N
138	2024-08-05	2024-12-12	13:10:00	14:50:00	WEDNESDAY	t	WEEKLY	\N	f	107	24	\N
139	2024-08-05	2024-12-12	09:20:00	11:00:00	MONDAY	t	WEEKLY	\N	f	108	26	\N
140	2024-08-05	2024-12-12	09:20:00	11:00:00	WEDNESDAY	t	WEEKLY	\N	f	108	22	\N
141	2024-08-05	2024-12-12	18:00:00	19:40:00	MONDAY	t	WEEKLY	\N	f	109	24	\N
142	2024-08-05	2024-12-12	18:00:00	19:40:00	WEDNESDAY	t	WEEKLY	\N	f	109	24	\N
144	2024-08-05	2024-12-12	11:10:00	12:50:00	FRIDAY	t	WEEKLY	\N	f	110	32	\N
145	2024-08-05	2024-12-12	09:20:00	11:00:00	WEDNESDAY	t	WEEKLY	\N	f	111	38	\N
146	2024-08-05	2024-12-12	11:10:00	12:50:00	FRIDAY	t	WEEKLY	\N	f	111	33	\N
147	2024-08-05	2024-12-12	09:20:00	12:50:00	WEDNESDAY	t	WEEKLY	\N	f	112	65	\N
148	2024-08-05	2024-12-12	09:20:00	11:00:00	TUESDAY	t	WEEKLY	\N	f	113	65	\N
149	2024-08-05	2024-12-12	07:30:00	09:10:00	THURSDAY	t	WEEKLY	\N	f	113	26	\N
150	2024-08-05	2024-12-12	07:30:00	09:10:00	MONDAY	t	WEEKLY	\N	f	114	26	\N
151	2024-08-05	2024-12-12	09:20:00	11:00:00	FRIDAY	t	WEEKLY	\N	f	114	26	\N
152	2024-08-05	2024-12-12	09:20:00	12:50:00	THURSDAY	t	WEEKLY	\N	f	115	39	\N
154	2024-08-05	2024-12-12	14:00:00	17:20:00	TUESDAY	t	WEEKLY	\N	f	117	24	\N
155	2024-08-05	2024-12-12	09:20:00	12:50:00	THURSDAY	t	WEEKLY	\N	f	118	24	\N
153	2024-08-05	2024-12-12	09:20:00	12:50:00	THURSDAY	t	WEEKLY	\N	f	116	39	\N
156	2024-08-05	2024-12-12	09:20:00	11:00:00	MONDAY	t	WEEKLY	\N	f	119	26	\N
158	2024-08-05	2024-12-12	11:10:00	12:50:00	MONDAY	t	WEEKLY	\N	f	120	74	\N
159	2024-08-05	2024-12-12	07:30:00	09:10:00	WEDNESDAY	t	WEEKLY	\N	f	120	74	\N
160	2024-08-05	2024-12-12	15:50:00	17:30:00	MONDAY	t	WEEKLY	\N	f	121	39	\N
161	2024-08-05	2024-12-12	14:00:00	15:40:00	THURSDAY	t	WEEKLY	\N	f	121	39	\N
162	2024-08-05	2024-12-12	16:50:00	18:30:00	MONDAY	t	WEEKLY	\N	f	122	74	\N
163	2024-08-05	2024-12-12	15:00:00	16:40:00	WEDNESDAY	t	WEEKLY	\N	f	122	74	\N
164	2024-08-05	2024-12-12	16:50:00	20:10:00	MONDAY	t	WEEKLY	\N	f	123	32	\N
165	2024-08-05	2024-12-12	16:50:00	18:30:00	TUESDAY	t	WEEKLY	\N	f	124	39	\N
166	2024-08-05	2024-12-12	16:50:00	18:30:00	THURSDAY	t	WEEKLY	\N	f	124	39	\N
167	2024-08-05	2024-12-12	13:10:00	16:40:00	WEDNESDAY	t	WEEKLY	\N	f	125	26	\N
168	2024-08-05	2024-12-12	18:40:00	20:20:00	TUESDAY	t	WEEKLY	\N	f	126	68	\N
169	2024-08-05	2024-12-12	08:30:00	10:10:00	SATURDAY	t	WEEKLY	\N	f	127	68	\N
177	2024-08-05	2024-12-12	18:50:00	22:30:00	TUESDAY	f	WEEKLY	\N	f	135	\N	\N
178	2024-08-05	2024-12-12	18:50:00	22:30:00	TUESDAY	f	WEEKLY	\N	f	136	\N	\N
179	2024-08-05	2024-12-12	09:20:00	11:00:00	WEDNESDAY	t	WEEKLY	\N	f	137	30	\N
180	2024-08-05	2024-12-12	13:10:00	14:50:00	FRIDAY	t	WEEKLY	\N	f	137	30	\N
181	2024-08-05	2024-12-12	09:20:00	11:00:00	WEDNESDAY	t	WEEKLY	\N	f	138	31	\N
182	2024-08-05	2024-12-12	13:10:00	14:50:00	FRIDAY	t	WEEKLY	\N	f	138	31	\N
183	2024-08-05	2024-12-12	09:20:00	11:00:00	WEDNESDAY	t	WEEKLY	\N	f	139	33	\N
184	2024-08-05	2024-12-12	13:10:00	14:50:00	FRIDAY	t	WEEKLY	\N	f	139	33	\N
185	2024-08-05	2024-12-12	13:10:00	15:50:00	MONDAY	t	WEEKLY	\N	f	140	29	\N
186	2024-08-05	2024-12-12	13:10:00	15:50:00	THURSDAY	t	WEEKLY	\N	f	141	29	\N
187	2024-08-05	2024-12-12	08:20:00	11:00:00	THURSDAY	t	WEEKLY	\N	f	142	29	\N
188	2024-08-05	2024-12-12	13:10:00	15:50:00	WEDNESDAY	t	WEEKLY	\N	f	143	29	\N
189	2024-08-05	2024-12-12	08:20:00	11:00:00	MONDAY	t	WEEKLY	\N	f	144	29	\N
190	2024-08-05	2024-12-12	13:10:00	15:50:00	TUESDAY	t	WEEKLY	\N	f	145	29	\N
191	2024-08-05	2024-12-12	15:00:00	17:30:00	FRIDAY	t	WEEKLY	\N	f	146	29	\N
585	2024-08-05	2024-12-11	11:10:00	12:50:00	FRIDAY	t	WEEKLY	\N	f	402	88	\N
583	2024-08-05	2024-12-11	11:10:00	12:50:00	TUESDAY	t	WEEKLY	\N	f	400	88	\N
584	2024-08-05	2024-12-11	12:00:00	14:00:00	WEDNESDAY	t	WEEKLY	\N	f	401	88	\N
598	2024-08-05	2024-12-12	15:00:00	16:40:00	MONDAY	t	WEEKLY	\N	f	414	89	\N
599	2024-08-05	2024-12-12	13:10:00	14:50:00	WEDNESDAY	t	WEEKLY	\N	f	414	89	\N
631	2024-08-05	2024-12-12	09:20:00	11:00:00	MONDAY	f	WEEKLY	\N	f	442	\N	\N
632	2024-08-05	2024-12-12	09:20:00	11:00:00	MONDAY	f	WEEKLY	\N	f	443	\N	\N
633	2024-08-05	2024-12-12	09:20:00	11:00:00	TUESDAY	f	WEEKLY	\N	f	444	\N	\N
634	2024-08-05	2024-12-12	09:20:00	11:00:00	TUESDAY	f	WEEKLY	\N	f	445	\N	\N
635	2024-08-05	2024-12-12	07:30:00	09:10:00	MONDAY	f	WEEKLY	\N	f	446	\N	\N
645	2024-08-05	2024-12-12	13:10:00	14:50:00	WEDNESDAY	f	WEEKLY	\N	f	455	\N	\N
644	2024-08-05	2024-12-12	09:20:00	11:00:00	MONDAY	t	WEEKLY	\N	f	455	53	\N
196	2024-08-05	2024-12-12	13:10:00	14:50:00	MONDAY	f	WEEKLY	\N	f	149	\N	\N
197	2024-08-05	2024-12-12	15:00:00	16:40:00	WEDNESDAY	f	WEEKLY	\N	f	149	\N	\N
198	2024-08-05	2024-12-12	13:10:00	14:50:00	MONDAY	f	WEEKLY	\N	f	150	\N	\N
199	2024-08-05	2024-12-12	15:00:00	16:40:00	WEDNESDAY	f	WEEKLY	\N	f	150	\N	\N
206	2024-08-05	2024-12-12	18:50:00	22:30:00	THURSDAY	f	WEEKLY	\N	f	154	\N	\N
207	2024-08-05	2024-12-12	14:00:00	17:40:00	TUESDAY	f	WEEKLY	\N	f	155	\N	\N
208	2024-08-05	2024-12-12	14:00:00	17:40:00	WEDNESDAY	f	WEEKLY	\N	f	156	\N	\N
209	2024-08-05	2024-12-12	14:00:00	17:40:00	FRIDAY	f	WEEKLY	\N	f	157	\N	\N
210	2024-08-05	2024-12-12	14:00:00	17:40:00	MONDAY	f	WEEKLY	\N	f	158	\N	\N
226	2024-08-05	2024-12-12	14:00:00	17:40:00	TUESDAY	f	WEEKLY	\N	f	169	\N	\N
587	2024-08-05	2024-12-12	13:10:00	14:50:00	TUESDAY	t	WEEKLY	\N	f	404	88	\N
247	2024-08-05	2024-12-12	13:10:00	14:50:00	MONDAY	t	WEEKLY	\N	f	182	47	\N
232	2024-08-05	2024-12-12	09:20:00	11:00:00	WEDNESDAY	f	WEEKLY	\N	f	172	\N	\N
239	2024-08-05	2024-12-12	07:30:00	09:10:00	MONDAY	f	WEEKLY	\N	f	178	\N	\N
240	2024-08-05	2024-12-12	07:30:00	09:10:00	TUESDAY	f	WEEKLY	\N	f	178	\N	\N
243	2024-08-05	2024-12-12	07:30:00	09:10:00	TUESDAY	f	WEEKLY	\N	f	180	\N	\N
244	2024-08-05	2024-12-12	07:30:00	09:10:00	WEDNESDAY	f	WEEKLY	\N	f	180	\N	\N
245	2024-08-05	2024-12-12	15:00:00	16:40:00	WEDNESDAY	f	WEEKLY	\N	f	181	\N	\N
246	2024-08-05	2024-12-12	15:00:00	16:40:00	FRIDAY	f	WEEKLY	\N	f	181	\N	\N
248	2024-08-05	2024-12-12	13:10:00	14:50:00	WEDNESDAY	f	WEEKLY	\N	f	182	\N	\N
249	2024-08-05	2024-12-12	15:00:00	16:40:00	MONDAY	f	WEEKLY	\N	f	183	\N	\N
250	2024-08-05	2024-12-12	15:00:00	16:40:00	WEDNESDAY	f	WEEKLY	\N	f	183	\N	\N
253	2024-08-05	2024-12-12	11:10:00	12:50:00	MONDAY	f	WEEKLY	\N	f	185	\N	\N
254	2024-08-05	2024-12-12	11:10:00	12:50:00	THURSDAY	f	WEEKLY	\N	f	185	\N	\N
255	2024-08-05	2024-12-12	11:10:00	12:50:00	WEDNESDAY	f	WEEKLY	\N	f	186	\N	\N
256	2024-08-05	2024-12-12	11:10:00	12:50:00	FRIDAY	f	WEEKLY	\N	f	186	\N	\N
258	2024-08-05	2024-12-12	16:00:00	17:40:00	FRIDAY	f	WEEKLY	\N	f	188	\N	\N
259	2024-08-05	2024-12-12	13:10:00	14:50:00	THURSDAY	f	WEEKLY	\N	f	189	\N	\N
260	2024-08-05	2024-12-12	13:10:00	14:50:00	THURSDAY	f	WEEKLY	\N	f	190	\N	\N
261	2024-08-05	2024-12-12	13:10:00	14:50:00	THURSDAY	f	WEEKLY	\N	f	191	\N	\N
273	2024-08-05	2024-12-12	13:10:00	14:50:00	THURSDAY	f	WEEKLY	\N	f	203	\N	\N
231	2024-08-05	2024-12-12	13:10:00	14:50:00	MONDAY	t	WEEKLY	\N	f	172	32	\N
1	2024-08-05	2024-12-12	15:00:00	16:40:00	MONDAY	t	WEEKLY	\N	f	1	38	\N
2	2024-08-05	2024-12-12	15:00:00	16:40:00	FRIDAY	t	WEEKLY	\N	f	1	38	\N
275	2024-08-05	2024-12-12	15:00:00	16:40:00	WEDNESDAY	t	WEEKLY	\N	f	205	67	\N
35	2024-08-05	2024-12-12	15:00:00	16:40:00	THURSDAY	t	WEEKLY	\N	f	33	27	\N
263	2024-08-05	2024-12-12	13:10:00	14:50:00	THURSDAY	t	WEEKLY	\N	f	193	32	\N
264	2024-08-05	2024-12-12	07:30:00	09:10:00	WEDNESDAY	t	WEEKLY	\N	f	194	32	\N
265	2024-08-05	2024-12-12	07:30:00	09:10:00	WEDNESDAY	t	WEEKLY	\N	f	195	32	\N
266	2024-08-05	2024-12-12	09:20:00	11:00:00	WEDNESDAY	t	WEEKLY	\N	f	196	32	\N
267	2024-08-05	2024-12-12	09:20:00	11:00:00	WEDNESDAY	t	WEEKLY	\N	f	197	32	\N
269	2024-08-05	2024-12-12	13:10:00	14:50:00	WEDNESDAY	t	WEEKLY	\N	f	199	32	\N
268	2024-08-05	2024-12-12	09:20:00	11:00:00	WEDNESDAY	t	WEEKLY	\N	f	198	69	\N
270	2024-08-05	2024-12-12	13:10:00	14:50:00	WEDNESDAY	t	WEEKLY	\N	f	200	32	\N
271	2024-08-05	2024-12-12	13:10:00	14:50:00	THURSDAY	t	WEEKLY	\N	f	201	32	\N
274	2024-08-05	2024-12-12	13:10:00	14:50:00	FRIDAY	t	WEEKLY	\N	f	204	32	\N
272	2024-08-05	2024-12-12	13:10:00	14:50:00	FRIDAY	t	WEEKLY	\N	f	202	32	\N
278	2024-08-05	2024-12-12	13:10:00	14:50:00	MONDAY	t	WEEKLY	\N	f	207	16	\N
279	2024-08-05	2024-12-12	15:00:00	16:40:00	THURSDAY	t	WEEKLY	\N	f	207	16	\N
280	2024-08-05	2024-12-12	15:00:00	16:40:00	MONDAY	t	WEEKLY	\N	f	208	17	\N
281	2024-08-05	2024-12-12	13:10:00	14:50:00	THURSDAY	t	WEEKLY	\N	f	208	17	\N
192	2024-08-05	2024-12-12	13:10:00	14:50:00	WEDNESDAY	t	WEEKLY	\N	f	147	38	\N
193	2024-08-05	2024-12-12	13:10:00	14:50:00	FRIDAY	t	WEEKLY	\N	f	147	65	\N
194	2024-08-05	2024-12-12	13:10:00	14:50:00	WEDNESDAY	t	WEEKLY	\N	f	148	22	\N
195	2024-08-05	2024-12-12	13:10:00	14:50:00	FRIDAY	t	WEEKLY	\N	f	148	21	\N
200	2024-08-05	2024-12-12	13:10:00	14:50:00	MONDAY	t	WEEKLY	\N	f	151	30	\N
201	2024-08-05	2024-12-12	15:00:00	16:40:00	WEDNESDAY	t	WEEKLY	\N	f	151	30	\N
202	2024-08-05	2024-12-12	13:10:00	14:50:00	MONDAY	t	WEEKLY	\N	f	152	31	\N
203	2024-08-05	2024-12-12	15:00:00	16:40:00	WEDNESDAY	t	WEEKLY	\N	f	152	31	\N
204	2024-08-05	2024-12-12	13:10:00	14:50:00	MONDAY	t	WEEKLY	\N	f	153	33	\N
205	2024-08-05	2024-12-12	15:00:00	16:40:00	WEDNESDAY	t	WEEKLY	\N	f	153	33	\N
211	2024-08-05	2024-12-12	12:00:00	12:50:00	SATURDAY	t	WEEKLY	\N	f	159	68	\N
212	2024-08-05	2024-12-12	13:10:00	14:00:00	SATURDAY	t	WEEKLY	\N	f	159	68	\N
213	2024-08-05	2024-12-12	09:10:00	10:00:00	SATURDAY	t	WEEKLY	\N	f	160	68	\N
214	2024-08-05	2024-12-12	08:20:00	12:00:00	THURSDAY	t	WEEKLY	\N	f	161	75	\N
215	2024-08-05	2024-12-12	08:20:00	12:00:00	TUESDAY	t	WEEKLY	\N	f	162	75	\N
216	2024-08-05	2024-12-12	08:20:00	12:00:00	WEDNESDAY	t	WEEKLY	\N	f	163	27	\N
217	2024-08-05	2024-12-12	14:00:00	17:40:00	THURSDAY	t	WEEKLY	\N	f	164	75	\N
218	2024-05-06	2024-08-16	10:20:00	12:00:00	MONDAY	t	WEEKLY	\N	f	165	23	\N
220	2024-05-06	2024-08-16	10:20:00	12:00:00	MONDAY	t	WEEKLY	\N	f	166	25	\N
221	2024-05-06	2024-08-16	08:20:00	10:00:00	WEDNESDAY	t	WEEKLY	\N	f	166	25	\N
222	2024-05-06	2024-08-16	08:20:00	10:00:00	MONDAY	t	WEEKLY	\N	f	167	23	\N
223	2024-05-06	2024-08-16	10:20:00	12:00:00	WEDNESDAY	t	WEEKLY	\N	f	167	23	\N
224	2024-05-06	2024-08-16	08:20:00	10:00:00	MONDAY	t	WEEKLY	\N	f	168	25	\N
225	2024-05-06	2024-08-16	10:20:00	12:00:00	WEDNESDAY	t	WEEKLY	\N	f	168	25	\N
235	2024-08-05	2024-12-12	09:20:00	11:00:00	TUESDAY	t	WEEKLY	\N	f	174	30	\N
236	2024-08-05	2024-12-12	09:20:00	11:00:00	TUESDAY	t	WEEKLY	\N	f	175	31	\N
237	2024-08-05	2024-12-12	09:20:00	11:00:00	TUESDAY	t	WEEKLY	\N	f	176	32	\N
238	2024-08-05	2024-12-12	09:20:00	11:00:00	TUESDAY	t	WEEKLY	\N	f	177	33	\N
241	2024-08-05	2024-12-12	07:30:00	09:10:00	MONDAY	t	WEEKLY	\N	f	179	38	\N
242	2024-08-05	2024-12-12	07:30:00	09:10:00	THURSDAY	t	WEEKLY	\N	f	179	38	\N
251	2024-08-05	2024-12-12	07:30:00	09:10:00	MONDAY	t	WEEKLY	\N	f	184	31	\N
252	2024-08-05	2024-12-12	07:30:00	09:10:00	THURSDAY	t	WEEKLY	\N	f	184	31	\N
257	2024-08-05	2024-12-12	11:10:00	12:50:00	TUESDAY	t	WEEKLY	\N	f	187	24	\N
262	2024-08-05	2024-12-12	11:10:00	12:50:00	FRIDAY	t	WEEKLY	\N	f	192	30	\N
296	2024-08-05	2024-12-12	07:30:00	09:20:00	MONDAY	f	WEEKLY	\N	f	216	\N	\N
297	2024-08-05	2024-12-12	09:20:00	11:00:00	WEDNESDAY	f	WEEKLY	\N	f	216	\N	\N
589	2024-08-05	2024-12-11	17:40:00	18:30:00	MONDAY	t	WEEKLY	\N	f	406	88	\N
580	2024-08-05	2024-12-11	07:30:00	11:00:00	FRIDAY	t	WEEKLY	\N	f	397	88	\N
588	2024-08-05	2024-12-11	13:10:00	16:40:00	THURSDAY	t	WEEKLY	\N	f	405	88	\N
592	2024-08-05	2024-12-11	11:10:00	12:50:00	MONDAY	t	WEEKLY	\N	f	408	89	\N
595	2024-08-05	2024-12-11	09:20:00	12:00:00	THURSDAY	t	WEEKLY	\N	f	411	89	\N
616	2024-08-05	2024-12-12	07:30:00	09:10:00	WEDNESDAY	t	WEEKLY	\N	f	429	93	\N
614	2024-08-05	2024-12-12	10:00:00	12:00:00	TUESDAY	t	WEEKLY	\N	f	428	93	\N
615	2024-08-05	2024-12-12	10:00:00	12:00:00	WEDNESDAY	t	WEEKLY	\N	f	428	93	\N
618	2024-08-05	2024-12-12	08:00:00	12:00:00	MONDAY	f	WEEKLY	\N	f	431	\N	\N
619	2024-08-05	2024-12-12	13:10:00	16:40:00	MONDAY	f	WEEKLY	\N	f	432	\N	\N
624	2024-08-05	2024-12-12	08:20:00	11:00:00	MONDAY	f	WEEKLY	\N	f	435	\N	\N
636	2024-08-05	2024-12-12	09:20:00	11:00:00	MONDAY	f	WEEKLY	\N	f	447	\N	\N
276	2024-08-05	2024-12-12	09:20:00	11:00:00	MONDAY	t	WEEKLY	\N	f	206	16	\N
277	2024-08-05	2024-12-12	07:30:00	09:10:00	THURSDAY	t	WEEKLY	\N	f	206	16	\N
282	2024-08-05	2024-12-12	07:30:00	09:10:00	MONDAY	t	WEEKLY	\N	f	209	17	\N
283	2024-08-05	2024-12-12	09:20:00	11:00:00	THURSDAY	t	WEEKLY	\N	f	209	17	\N
284	2024-08-05	2024-12-12	09:20:00	11:00:00	MONDAY	t	WEEKLY	\N	f	210	18	\N
285	2024-08-05	2024-12-12	07:30:00	09:10:00	THURSDAY	t	WEEKLY	\N	f	210	18	\N
286	2024-08-05	2024-12-12	07:30:00	09:10:00	MONDAY	t	WEEKLY	\N	f	211	69	\N
287	2024-08-05	2024-12-12	09:20:00	11:00:00	THURSDAY	t	WEEKLY	\N	f	211	69	\N
288	2024-08-05	2024-12-12	09:20:00	11:00:00	MONDAY	t	WEEKLY	\N	f	212	20	\N
289	2024-08-05	2024-12-12	07:30:00	09:10:00	WEDNESDAY	t	WEEKLY	\N	f	212	20	\N
290	2024-08-05	2024-12-12	07:30:00	09:10:00	TUESDAY	t	WEEKLY	\N	f	213	17	\N
291	2024-08-05	2024-12-12	09:20:00	11:00:00	FRIDAY	t	WEEKLY	\N	f	213	17	\N
292	2024-08-05	2024-12-12	09:20:00	11:00:00	TUESDAY	t	WEEKLY	\N	f	214	16	\N
293	2024-08-05	2024-12-12	07:30:00	09:10:00	FRIDAY	t	WEEKLY	\N	f	214	16	\N
294	2024-08-05	2024-12-12	15:00:00	16:40:00	TUESDAY	t	WEEKLY	\N	f	215	18	\N
295	2024-08-05	2024-12-12	07:30:00	09:10:00	FRIDAY	t	WEEKLY	\N	f	215	18	\N
298	2024-08-05	2024-12-12	07:30:00	09:10:00	MONDAY	t	WEEKLY	\N	f	217	19	\N
299	2024-08-05	2024-12-12	09:20:00	11:00:00	WEDNESDAY	t	WEEKLY	\N	f	217	19	\N
320	2024-08-05	2024-12-12	13:10:00	14:50:00	TUESDAY	t	WEEKLY	\N	f	228	11	\N
321	2024-08-05	2024-12-12	15:00:00	16:40:00	THURSDAY	t	WEEKLY	\N	f	228	11	\N
322	2024-08-05	2024-12-12	15:00:00	16:40:00	TUESDAY	t	WEEKLY	\N	f	229	12	\N
323	2024-08-05	2024-12-12	13:10:00	14:50:00	THURSDAY	t	WEEKLY	\N	f	229	12	\N
324	2024-08-05	2024-12-12	13:10:00	14:50:00	TUESDAY	t	WEEKLY	\N	f	230	13	\N
325	2024-08-05	2024-12-12	15:00:00	16:40:00	THURSDAY	t	WEEKLY	\N	f	230	13	\N
326	2024-08-05	2024-12-12	15:00:00	16:40:00	TUESDAY	t	WEEKLY	\N	f	231	7	\N
327	2024-08-05	2024-12-12	13:10:00	14:50:00	THURSDAY	t	WEEKLY	\N	f	231	7	\N
328	2024-08-05	2024-12-12	13:10:00	14:50:00	TUESDAY	t	WEEKLY	\N	f	232	69	\N
329	2024-08-05	2024-12-12	15:00:00	16:40:00	THURSDAY	t	WEEKLY	\N	f	232	69	\N
330	2024-08-05	2024-12-12	15:00:00	16:40:00	TUESDAY	t	WEEKLY	\N	f	233	20	\N
331	2024-08-05	2024-12-12	13:10:00	14:50:00	THURSDAY	t	WEEKLY	\N	f	233	20	\N
332	2024-08-05	2024-12-12	13:10:00	14:50:00	TUESDAY	t	WEEKLY	\N	f	234	9	\N
333	2024-08-05	2024-12-12	15:00:00	16:40:00	THURSDAY	t	WEEKLY	\N	f	234	9	\N
334	2024-08-05	2024-12-12	15:00:00	16:40:00	TUESDAY	t	WEEKLY	\N	f	235	3	\N
335	2024-08-05	2024-12-12	13:10:00	14:50:00	THURSDAY	t	WEEKLY	\N	f	235	3	\N
336	2024-08-05	2024-12-12	15:00:00	16:40:00	TUESDAY	t	WEEKLY	\N	f	236	8	\N
337	2024-08-05	2024-12-12	13:10:00	14:50:00	THURSDAY	t	WEEKLY	\N	f	236	8	\N
338	2024-08-05	2024-12-12	11:10:00	12:50:00	MONDAY	t	WEEKLY	\N	f	237	16	\N
617	2024-08-05	2024-12-12	08:00:00	12:00:00	MONDAY	t	WEEKLY	\N	f	430	45	\N
345	2024-08-05	2024-12-12	15:00:00	16:40:00	TUESDAY	t	WEEKLY	\N	f	241	2	\N
346	2024-08-05	2024-12-12	13:10:00	14:50:00	THURSDAY	t	WEEKLY	\N	f	241	2	\N
347	2024-08-05	2024-12-12	13:10:00	14:50:00	TUESDAY	t	WEEKLY	\N	f	242	2	\N
348	2024-08-05	2024-12-12	15:00:00	16:40:00	THURSDAY	t	WEEKLY	\N	f	242	2	\N
349	2024-08-05	2024-12-12	15:00:00	16:40:00	TUESDAY	t	WEEKLY	\N	f	243	3	\N
350	2024-08-05	2024-12-12	13:10:00	14:50:00	THURSDAY	t	WEEKLY	\N	f	243	3	\N
351	2024-08-05	2024-12-12	13:10:00	14:50:00	TUESDAY	t	WEEKLY	\N	f	244	3	\N
352	2024-08-05	2024-12-12	15:00:00	16:40:00	THURSDAY	t	WEEKLY	\N	f	244	3	\N
353	2024-08-05	2024-12-12	15:00:00	16:40:00	TUESDAY	t	WEEKLY	\N	f	245	4	\N
354	2024-08-05	2024-12-12	13:10:00	14:50:00	THURSDAY	t	WEEKLY	\N	f	245	4	\N
355	2024-08-05	2024-12-12	13:10:00	14:50:00	TUESDAY	t	WEEKLY	\N	f	246	4	\N
356	2024-08-05	2024-12-12	15:00:00	16:40:00	THURSDAY	t	WEEKLY	\N	f	246	4	\N
357	2024-08-05	2024-12-12	15:00:00	16:40:00	TUESDAY	t	WEEKLY	\N	f	247	5	\N
358	2024-08-05	2024-12-12	13:10:00	14:50:00	THURSDAY	t	WEEKLY	\N	f	247	5	\N
359	2024-08-05	2024-12-12	13:10:00	14:50:00	TUESDAY	t	WEEKLY	\N	f	248	5	\N
360	2024-08-05	2024-12-12	15:00:00	16:40:00	THURSDAY	t	WEEKLY	\N	f	248	5	\N
361	2024-08-05	2024-12-12	13:10:00	14:50:00	TUESDAY	t	WEEKLY	\N	f	249	6	\N
362	2024-08-05	2024-12-12	15:00:00	16:40:00	THURSDAY	t	WEEKLY	\N	f	249	6	\N
363	2024-08-05	2024-12-12	15:00:00	16:40:00	TUESDAY	t	WEEKLY	\N	f	250	6	\N
364	2024-08-05	2024-12-12	13:10:00	14:50:00	THURSDAY	t	WEEKLY	\N	f	250	6	\N
371	2024-08-05	2024-12-12	08:20:00	11:00:00	TUESDAY	t	WEEKLY	\N	f	255	3	\N
372	2024-08-05	2024-12-12	08:20:00	11:00:00	FRIDAY	t	WEEKLY	\N	f	255	3	\N
373	2024-08-05	2024-12-12	08:20:00	11:00:00	TUESDAY	t	WEEKLY	\N	f	256	4	\N
374	2024-08-05	2024-12-12	08:20:00	11:00:00	FRIDAY	t	WEEKLY	\N	f	256	4	\N
375	2024-08-05	2024-12-12	08:20:00	11:00:00	TUESDAY	t	WEEKLY	\N	f	257	13	\N
376	2024-08-05	2024-12-12	08:20:00	11:00:00	FRIDAY	t	WEEKLY	\N	f	257	13	\N
377	2024-08-05	2024-12-12	08:20:00	11:00:00	TUESDAY	t	WEEKLY	\N	f	258	12	\N
378	2024-08-05	2024-12-12	08:20:00	11:00:00	FRIDAY	t	WEEKLY	\N	f	258	12	\N
379	2024-08-05	2024-12-12	08:20:00	11:00:00	TUESDAY	t	WEEKLY	\N	f	259	11	\N
380	2024-08-05	2024-12-12	08:20:00	11:00:00	FRIDAY	t	WEEKLY	\N	f	259	11	\N
383	2024-08-05	2024-12-12	08:20:00	11:00:00	TUESDAY	f	WEEKLY	\N	f	261	\N	\N
384	2024-08-05	2024-12-12	08:20:00	11:00:00	FRIDAY	f	WEEKLY	\N	f	261	\N	\N
381	2024-08-05	2024-12-12	08:20:00	11:00:00	TUESDAY	t	WEEKLY	\N	f	260	10	\N
382	2024-08-05	2024-12-12	08:20:00	11:00:00	FRIDAY	t	WEEKLY	\N	f	260	10	\N
385	2024-08-05	2024-12-12	08:20:00	11:00:00	MONDAY	t	WEEKLY	\N	f	262	10	\N
386	2024-08-05	2024-12-12	08:20:00	11:00:00	WEDNESDAY	t	WEEKLY	\N	f	262	10	\N
387	2024-08-05	2024-12-12	08:20:00	11:00:00	MONDAY	t	WEEKLY	\N	f	263	11	\N
388	2024-08-05	2024-12-12	08:20:00	11:00:00	WEDNESDAY	t	WEEKLY	\N	f	263	11	\N
389	2024-08-05	2024-12-12	08:20:00	11:00:00	MONDAY	t	WEEKLY	\N	f	264	13	\N
390	2024-08-05	2024-12-12	08:20:00	11:00:00	WEDNESDAY	t	WEEKLY	\N	f	264	13	\N
391	2024-08-05	2024-12-12	08:20:00	11:00:00	TUESDAY	t	WEEKLY	\N	f	265	8	\N
392	2024-08-05	2024-12-12	08:20:00	11:00:00	FRIDAY	t	WEEKLY	\N	f	265	8	\N
393	2024-08-05	2024-12-12	08:20:00	11:00:00	TUESDAY	t	WEEKLY	\N	f	266	9	\N
394	2024-08-05	2024-12-12	08:20:00	11:00:00	FRIDAY	t	WEEKLY	\N	f	266	9	\N
157	2024-08-05	2024-12-12	07:30:00	09:10:00	TUESDAY	t	WEEKLY	\N	f	119	65	\N
472	2024-08-05	2024-12-11	13:10:00	14:50:00	MONDAY	t	WEEKLY	\N	f	289	4	\N
471	2024-08-05	2024-12-11	09:20:00	11:00:00	MONDAY	t	WEEKLY	\N	f	289	4	\N
54	2024-08-05	2024-12-12	16:50:00	18:30:00	THURSDAY	t	WEEKLY	\N	f	51	27	\N
399	2024-08-05	2024-12-12	15:00:00	16:40:00	MONDAY	t	WEEKLY	\N	f	269	10	\N
400	2024-08-05	2024-12-12	13:10:00	14:50:00	MONDAY	t	WEEKLY	\N	f	270	8	\N
401	2024-08-05	2024-12-12	15:00:00	16:40:00	MONDAY	t	WEEKLY	\N	f	271	9	\N
402	2024-08-05	2024-12-12	13:10:00	14:50:00	MONDAY	t	WEEKLY	\N	f	272	9	\N
403	2024-08-05	2024-12-12	13:10:00	14:50:00	MONDAY	t	WEEKLY	\N	f	273	12	\N
404	2024-08-05	2024-12-12	13:10:00	14:50:00	MONDAY	t	WEEKLY	\N	f	274	11	\N
405	2024-08-05	2024-12-12	09:20:00	11:00:00	THURSDAY	t	WEEKLY	\N	f	274	11	\N
406	2024-08-05	2024-12-12	13:10:00	14:50:00	MONDAY	t	WEEKLY	\N	f	275	10	\N
407	2024-08-05	2024-12-12	09:20:00	11:00:00	THURSDAY	t	WEEKLY	\N	f	275	10	\N
408	2024-08-05	2024-12-12	13:10:00	14:50:00	MONDAY	t	WEEKLY	\N	f	276	13	\N
409	2024-08-05	2024-12-12	09:20:00	11:00:00	THURSDAY	t	WEEKLY	\N	f	276	13	\N
410	2024-08-05	2024-12-12	15:00:00	16:40:00	MONDAY	t	WEEKLY	\N	f	277	12	\N
411	2024-08-05	2024-12-12	09:20:00	11:00:00	THURSDAY	t	WEEKLY	\N	f	277	12	\N
412	2024-08-05	2024-12-12	15:00:00	16:40:00	MONDAY	t	WEEKLY	\N	f	278	10	\N
413	2024-08-05	2024-12-12	13:10:00	14:50:00	THURSDAY	t	WEEKLY	\N	f	278	10	\N
414	2024-08-05	2024-12-12	15:00:00	16:40:00	MONDAY	t	WEEKLY	\N	f	279	11	\N
415	2024-08-05	2024-12-12	13:10:00	14:50:00	WEDNESDAY	t	WEEKLY	\N	f	279	11	\N
586	2024-08-05	2024-12-12	13:10:00	14:50:00	MONDAY	t	WEEKLY	\N	f	403	88	\N
416	2024-08-05	2024-12-11	15:00:00	16:40:00	MONDAY	t	WEEKLY	\N	f	280	71	\N
417	2024-08-05	2024-12-11	15:00:00	16:40:00	MONDAY	t	WEEKLY	\N	f	281	70	\N
418	2024-08-05	2024-12-11	13:10:00	14:50:00	MONDAY	t	WEEKLY	\N	f	282	71	\N
434	2024-08-05	2024-12-12	15:00:00	16:40:00	MONDAY	t	WEEKLY	\N	f	292	16	\N
435	2024-08-05	2024-12-12	13:10:00	14:50:00	THURSDAY	t	WEEKLY	\N	f	292	16	\N
450	2024-08-05	2024-12-12	13:10:00	14:50:00	TUESDAY	t	WEEKLY	\N	f	300	18	\N
451	2024-08-05	2024-12-12	09:20:00	11:00:00	FRIDAY	t	WEEKLY	\N	f	300	18	\N
473	2024-08-05	2024-12-12	18:40:00	20:20:00	MONDAY	t	WEEKLY	\N	f	304	68	\N
79	2024-08-05	2024-12-12	14:00:00	15:40:00	WEDNESDAY	t	WEEKLY	\N	f	66	21	\N
89	2024-08-05	2024-12-12	09:10:00	12:10:00	WEDNESDAY	t	WEEKLY	\N	f	74	21	\N
91	2024-05-06	2024-08-16	08:20:00	10:00:00	THURSDAY	t	WEEKLY	\N	f	75	23	\N
128	2024-08-05	2024-12-12	09:20:00	11:00:00	FRIDAY	t	WEEKLY	\N	f	102	30	\N
452	2024-08-05	2024-12-12	09:20:00	11:00:00	MONDAY	f	WEEKLY	\N	f	301	\N	\N
453	2024-08-05	2024-12-12	07:30:00	09:10:00	WEDNESDAY	f	WEEKLY	\N	f	301	\N	\N
446	2024-08-05	2024-12-12	09:20:00	11:00:00	TUESDAY	t	WEEKLY	\N	f	298	17	\N
447	2024-08-05	2024-12-12	07:30:00	09:10:00	FRIDAY	t	WEEKLY	\N	f	298	17	\N
448	2024-08-05	2024-12-12	07:30:00	09:10:00	TUESDAY	t	WEEKLY	\N	f	299	16	\N
449	2024-08-05	2024-12-12	09:20:00	11:00:00	FRIDAY	t	WEEKLY	\N	f	299	16	\N
432	2024-08-05	2024-12-12	07:30:00	09:10:00	MONDAY	t	WEEKLY	\N	f	291	16	\N
433	2024-08-05	2024-12-12	09:20:00	11:00:00	THURSDAY	t	WEEKLY	\N	f	291	16	\N
436	2024-08-05	2024-12-12	13:10:00	14:50:00	MONDAY	t	WEEKLY	\N	f	293	17	\N
437	2024-08-05	2024-12-12	15:00:00	16:40:00	THURSDAY	t	WEEKLY	\N	f	293	17	\N
438	2024-08-05	2024-12-12	09:20:00	11:00:00	MONDAY	t	WEEKLY	\N	f	294	17	\N
439	2024-08-05	2024-12-12	07:30:00	09:10:00	THURSDAY	t	WEEKLY	\N	f	294	17	\N
440	2024-08-05	2024-12-12	07:30:00	09:10:00	MONDAY	t	WEEKLY	\N	f	295	18	\N
441	2024-08-05	2024-12-12	09:20:00	11:00:00	THURSDAY	t	WEEKLY	\N	f	295	18	\N
444	2024-08-05	2024-12-12	07:30:00	09:10:00	MONDAY	t	WEEKLY	\N	f	297	20	\N
445	2024-08-05	2024-12-12	09:20:00	11:00:00	WEDNESDAY	t	WEEKLY	\N	f	297	20	\N
442	2024-08-05	2024-12-12	09:20:00	11:00:00	MONDAY	t	WEEKLY	\N	f	296	69	\N
443	2024-08-05	2024-12-12	07:30:00	09:10:00	THURSDAY	t	WEEKLY	\N	f	296	69	\N
454	2024-08-05	2024-12-12	09:20:00	11:00:00	MONDAY	t	WEEKLY	\N	f	302	19	\N
455	2024-08-05	2024-12-12	07:30:00	09:10:00	WEDNESDAY	t	WEEKLY	\N	f	302	19	\N
469	2024-08-05	2024-12-12	09:20:00	11:00:00	MONDAY	t	WEEKLY	\N	f	251	2	\N
470	2024-08-05	2024-12-12	13:10:00	14:50:00	WEDNESDAY	t	WEEKLY	\N	f	251	2	\N
395	2024-08-05	2024-12-12	09:20:00	11:00:00	TUESDAY	t	WEEKLY	\N	f	267	7	\N
396	2024-08-05	2024-12-12	09:20:00	11:00:00	WEDNESDAY	t	WEEKLY	\N	f	267	7	\N
397	2024-08-05	2024-12-12	09:20:00	11:00:00	TUESDAY	t	WEEKLY	\N	f	268	5	\N
398	2024-08-05	2024-12-12	09:20:00	11:00:00	WEDNESDAY	t	WEEKLY	\N	f	268	5	\N
468	2024-08-05	2024-12-12	17:00:00	18:40:00	FRIDAY	t	WEEKLY	\N	f	238	4	\N
219	2024-05-06	2024-08-16	08:20:00	10:00:00	WEDNESDAY	t	WEEKLY	\N	f	165	23	\N
474	2024-09-02	2024-12-13	14:00:00	15:40:00	WEDNESDAY	t	WEEKLY	\N	f	305	23	\N
475	2024-09-02	2024-12-13	10:20:00	12:00:00	FRIDAY	t	WEEKLY	\N	f	305	23	\N
477	2024-08-05	2024-12-12	13:10:00	16:40:00	WEDNESDAY	t	WEEKLY	\N	f	307	76	\N
478	2024-08-05	2024-12-12	13:10:00	14:50:00	MONDAY	t	WEEKLY	\N	f	308	76	\N
479	2024-08-05	2024-12-12	13:10:00	16:40:00	TUESDAY	t	WEEKLY	\N	f	309	77	\N
480	2024-08-05	2024-12-12	13:10:00	16:40:00	TUESDAY	t	WEEKLY	\N	f	310	77	\N
481	2024-08-05	2024-12-12	13:10:00	16:40:00	FRIDAY	t	WEEKLY	\N	f	311	77	\N
482	2024-08-05	2024-12-12	13:10:00	16:40:00	FRIDAY	t	WEEKLY	\N	f	312	77	\N
483	2024-08-05	2024-12-12	07:30:00	11:00:00	THURSDAY	t	WEEKLY	\N	f	313	78	\N
484	2024-08-05	2024-12-12	07:30:00	11:00:00	THURSDAY	t	WEEKLY	\N	f	314	78	\N
485	2024-08-05	2024-12-12	13:10:00	16:40:00	FRIDAY	t	WEEKLY	\N	f	315	78	\N
486	2024-08-05	2024-12-12	13:10:00	16:40:00	FRIDAY	t	WEEKLY	\N	f	316	78	\N
495	2024-08-05	2024-12-12	09:20:00	11:00:00	WEDNESDAY	t	WEEKLY	\N	f	323	80	\N
496	2024-08-05	2024-12-12	09:20:00	11:00:00	WEDNESDAY	t	WEEKLY	\N	f	324	81	\N
497	2024-08-05	2024-12-12	09:20:00	11:00:00	MONDAY	t	WEEKLY	\N	f	325	80	\N
498	2024-08-05	2024-12-12	09:20:00	11:00:00	MONDAY	t	WEEKLY	\N	f	326	76	\N
499	2024-08-05	2024-12-12	14:00:00	17:20:00	MONDAY	t	WEEKLY	\N	f	327	79	\N
500	2024-08-05	2024-12-12	14:00:00	17:20:00	MONDAY	t	WEEKLY	\N	f	328	79	\N
501	2024-08-05	2024-12-12	07:30:00	11:00:00	TUESDAY	t	WEEKLY	\N	f	329	80	\N
502	2024-08-05	2024-12-12	07:30:00	11:00:00	TUESDAY	t	WEEKLY	\N	f	330	80	\N
503	2024-08-05	2024-12-12	07:30:00	11:00:00	WEDNESDAY	t	WEEKLY	\N	f	331	82	\N
504	2024-08-05	2024-12-12	07:30:00	11:00:00	WEDNESDAY	t	WEEKLY	\N	f	332	82	\N
505	2024-08-05	2024-12-12	07:30:00	11:00:00	THURSDAY	t	WEEKLY	\N	f	333	79	\N
506	2024-08-05	2024-12-12	07:30:00	11:00:00	THURSDAY	t	WEEKLY	\N	f	334	79	\N
507	2024-08-05	2024-12-12	07:30:00	11:00:00	THURSDAY	t	WEEKLY	\N	f	335	79	\N
508	2024-08-05	2024-12-12	07:30:00	11:00:00	FRIDAY	t	WEEKLY	\N	f	336	80	\N
509	2024-08-05	2024-12-12	07:30:00	11:00:00	FRIDAY	t	WEEKLY	\N	f	337	80	\N
510	2024-08-05	2024-12-12	07:30:00	11:00:00	FRIDAY	t	WEEKLY	\N	f	338	80	\N
511	2024-08-05	2024-12-12	13:10:00	16:40:00	FRIDAY	t	WEEKLY	\N	f	339	79	\N
512	2024-08-05	2024-12-12	13:10:00	16:40:00	FRIDAY	t	WEEKLY	\N	f	340	79	\N
519	2024-08-05	2024-12-12	09:20:00	11:00:00	TUESDAY	t	WEEKLY	\N	f	346	81	\N
520	2024-08-05	2024-12-12	07:30:00	09:10:00	FRIDAY	t	WEEKLY	\N	f	346	81	\N
521	2024-08-05	2024-12-12	09:20:00	11:00:00	WEDNESDAY	t	WEEKLY	\N	f	347	84	\N
522	2024-08-05	2024-12-12	09:20:00	11:00:00	FRIDAY	t	WEEKLY	\N	f	347	84	\N
523	2024-08-05	2024-12-12	09:20:00	11:00:00	WEDNESDAY	t	WEEKLY	\N	f	348	83	\N
524	2024-08-05	2024-12-12	09:20:00	11:00:00	FRIDAY	t	WEEKLY	\N	f	348	83	\N
525	2024-08-05	2024-12-12	13:10:00	14:50:00	TUESDAY	t	WEEKLY	\N	f	349	80	\N
526	2024-08-05	2024-12-12	13:10:00	14:50:00	FRIDAY	t	WEEKLY	\N	f	349	80	\N
527	2024-08-05	2024-12-12	13:10:00	14:50:00	TUESDAY	t	WEEKLY	\N	f	350	81	\N
528	2024-08-05	2024-12-12	13:10:00	14:50:00	FRIDAY	t	WEEKLY	\N	f	350	81	\N
529	2024-08-05	2024-12-12	13:10:00	16:40:00	TUESDAY	t	WEEKLY	\N	f	351	78	\N
530	2024-08-05	2024-12-12	13:10:00	16:40:00	TUESDAY	t	WEEKLY	\N	f	352	78	\N
531	2024-08-05	2024-12-12	13:10:00	16:40:00	WEDNESDAY	t	WEEKLY	\N	f	353	78	\N
532	2024-08-05	2024-12-12	13:10:00	16:40:00	WEDNESDAY	t	WEEKLY	\N	f	354	78	\N
533	2024-08-05	2024-12-12	13:10:00	16:40:00	MONDAY	t	WEEKLY	\N	f	355	78	\N
534	2024-08-05	2024-12-12	13:10:00	16:40:00	THURSDAY	t	WEEKLY	\N	f	356	78	\N
535	2024-08-05	2024-12-12	09:20:00	11:00:00	FRIDAY	t	WEEKLY	\N	f	357	81	\N
536	2024-08-05	2024-12-12	15:00:00	18:30:00	MONDAY	t	WEEKLY	\N	f	358	77	\N
537	2024-08-05	2024-12-12	15:00:00	18:30:00	MONDAY	t	WEEKLY	\N	f	359	77	\N
538	2024-08-05	2024-12-12	07:30:00	10:10:00	THURSDAY	t	WEEKLY	\N	f	360	81	\N
539	2024-08-05	2024-12-12	14:00:00	17:30:00	TUESDAY	t	WEEKLY	\N	f	361	85	\N
540	2024-08-05	2024-12-12	14:00:00	17:30:00	TUESDAY	t	WEEKLY	\N	f	362	85	\N
541	2024-08-05	2024-12-12	14:00:00	17:30:00	THURSDAY	t	WEEKLY	\N	f	363	85	\N
542	2024-08-05	2024-12-12	14:00:00	17:30:00	THURSDAY	t	WEEKLY	\N	f	364	85	\N
543	2024-08-05	2024-12-12	13:10:00	14:50:00	FRIDAY	t	WEEKLY	\N	f	365	76	\N
556	2024-08-05	2024-12-12	14:00:00	17:30:00	TUESDAY	t	WEEKLY	\N	f	376	79	\N
557	2024-08-05	2024-12-12	14:00:00	17:30:00	TUESDAY	t	WEEKLY	\N	f	377	79	\N
558	2024-08-05	2024-12-12	09:20:00	12:50:00	THURSDAY	t	WEEKLY	\N	f	378	80	\N
582	2024-08-05	2024-12-12	09:20:00	12:00:00	MONDAY	t	WEEKLY	\N	f	399	88	\N
597	2024-08-05	2024-12-11	10:10:00	11:50:00	FRIDAY	t	WEEKLY	\N	f	413	89	\N
612	2024-08-05	2024-12-12	10:10:00	12:00:00	THURSDAY	t	WEEKLY	\N	f	426	91	\N
613	2024-08-05	2024-12-12	14:00:00	16:40:00	FRIDAY	t	WEEKLY	\N	f	427	91	\N
620	2024-08-05	2024-12-11	09:20:00	11:00:00	MONDAY	f	WEEKLY	\N	f	433	\N	\N
621	2024-08-05	2024-12-11	09:20:00	11:00:00	TUESDAY	f	WEEKLY	\N	f	433	\N	\N
625	2024-08-05	2024-12-12	09:20:00	11:00:00	MONDAY	f	WEEKLY	\N	f	436	\N	\N
626	2024-08-05	2024-12-12	09:20:00	11:00:00	MONDAY	f	WEEKLY	\N	f	437	\N	\N
627	2024-08-05	2024-12-12	07:30:00	09:10:00	FRIDAY	f	WEEKLY	\N	f	438	\N	\N
628	2024-08-05	2024-12-12	07:30:00	09:10:00	FRIDAY	f	WEEKLY	\N	f	439	\N	\N
629	2024-08-05	2024-12-12	13:10:00	15:50:00	MONDAY	f	WEEKLY	\N	f	440	\N	\N
630	2024-08-05	2024-12-12	13:10:00	15:50:00	MONDAY	f	WEEKLY	\N	f	441	\N	\N
637	2024-08-05	2024-12-12	13:10:00	16:40:00	MONDAY	f	WEEKLY	\N	f	448	\N	\N
513	2024-08-05	2024-12-12	08:20:00	12:00:00	WEDNESDAY	f	WEEKLY	\N	f	341	\N	\N
517	2024-08-05	2024-12-12	07:30:00	09:10:00	MONDAY	t	WEEKLY	\N	f	345	76	\N
518	2024-08-05	2024-12-12	07:30:00	09:10:00	WEDNESDAY	t	WEEKLY	\N	f	345	76	\N
487	2024-08-05	2024-12-12	10:10:00	11:50:00	MONDAY	t	WEEKLY	\N	f	317	86	\N
488	2024-08-05	2024-12-12	10:10:00	11:50:00	WEDNESDAY	t	WEEKLY	\N	f	317	86	\N
489	2024-08-05	2024-12-12	09:20:00	11:00:00	MONDAY	t	WEEKLY	\N	f	318	81	\N
490	2024-08-05	2024-12-12	10:10:00	11:50:00	WEDNESDAY	t	WEEKLY	\N	f	318	81	\N
491	2024-08-05	2024-12-12	13:10:00	16:40:00	MONDAY	t	WEEKLY	\N	f	319	85	\N
492	2024-08-05	2024-12-12	13:10:00	16:40:00	MONDAY	t	WEEKLY	\N	f	320	85	\N
493	2024-08-05	2024-12-12	13:10:00	16:40:00	WEDNESDAY	t	WEEKLY	\N	f	321	85	\N
494	2024-08-05	2024-12-12	13:10:00	16:40:00	WEDNESDAY	t	WEEKLY	\N	f	322	85	\N
544	2024-08-05	2024-12-12	07:30:00	09:10:00	TUESDAY	t	WEEKLY	\N	f	366	84	\N
559	2024-08-05	2024-12-12	09:20:00	11:00:00	WEDNESDAY	t	WEEKLY	\N	f	379	78	\N
560	2024-08-05	2024-12-12	07:30:00	09:10:00	FRIDAY	t	WEEKLY	\N	f	379	78	\N
552	2024-08-05	2024-12-12	13:10:00	16:40:00	TUESDAY	t	WEEKLY	\N	f	373	84	\N
548	2024-08-05	2024-12-12	13:10:00	14:50:00	THURSDAY	t	WEEKLY	\N	f	370	76	\N
549	2024-08-05	2024-12-12	15:00:00	16:40:00	FRIDAY	t	WEEKLY	\N	f	370	76	\N
550	2024-08-05	2024-12-12	08:20:00	12:00:00	THURSDAY	t	WEEKLY	\N	f	371	84	\N
551	2024-08-05	2024-12-12	16:50:00	18:30:00	FRIDAY	t	WEEKLY	\N	f	372	81	\N
554	2024-08-05	2024-12-12	15:00:00	16:40:00	MONDAY	t	WEEKLY	\N	f	375	81	\N
555	2024-08-05	2024-12-12	13:10:00	14:50:00	WEDNESDAY	t	WEEKLY	\N	f	375	81	\N
545	2024-08-05	2024-12-12	11:10:00	12:00:00	SATURDAY	t	WEEKLY	\N	f	367	84	\N
546	2024-08-05	2024-12-12	11:10:00	12:00:00	FRIDAY	t	WEEKLY	\N	f	368	79	\N
547	2024-08-05	2024-12-12	12:00:00	12:50:00	FRIDAY	t	WEEKLY	\N	f	369	79	\N
561	2024-08-05	2024-12-12	11:10:00	12:50:00	FRIDAY	t	WEEKLY	\N	f	380	80	\N
562	2024-08-05	2024-12-12	11:10:00	12:50:00	FRIDAY	t	WEEKLY	\N	f	381	80	\N
590	2024-08-05	2024-12-11	09:20:00	11:00:00	MONDAY	t	WEEKLY	\N	f	407	89	\N
591	2024-08-05	2024-12-11	11:10:00	12:50:00	TUESDAY	t	WEEKLY	\N	f	407	89	\N
593	2024-08-05	2024-12-11	09:20:00	11:00:00	TUESDAY	t	WEEKLY	\N	f	409	89	\N
594	2024-08-05	2024-12-11	09:20:00	11:00:00	WEDNESDAY	t	WEEKLY	\N	f	410	89	\N
638	2024-08-05	2024-12-12	07:30:00	09:10:00	MONDAY	f	WEEKLY	\N	f	449	\N	\N
639	2024-08-05	2024-12-12	09:20:00	11:00:00	THURSDAY	f	WEEKLY	\N	f	450	\N	\N
640	2024-08-05	2024-12-12	09:20:00	11:00:00	THURSDAY	f	WEEKLY	\N	f	451	\N	\N
641	2024-08-05	2024-12-12	09:20:00	11:00:00	FRIDAY	f	WEEKLY	\N	f	452	\N	\N
642	2024-08-05	2024-12-12	13:10:00	14:50:00	FRIDAY	f	WEEKLY	\N	f	453	\N	\N
476	2024-08-05	2024-12-12	13:10:00	16:40:00	WEDNESDAY	t	WEEKLY	\N	f	306	76	\N
514	2024-08-05	2024-12-12	15:00:00	16:40:00	WEDNESDAY	t	WEEKLY	\N	f	342	81	\N
515	2024-08-05	2024-12-12	15:00:00	16:40:00	THURSDAY	t	WEEKLY	\N	f	343	81	\N
516	2024-08-05	2024-12-12	15:00:00	16:40:00	FRIDAY	t	WEEKLY	\N	f	344	81	\N
553	2024-08-05	2024-12-12	07:30:00	11:00:00	SATURDAY	t	WEEKLY	\N	f	374	84	\N
563	2024-08-05	2024-12-12	13:10:00	14:50:00	FRIDAY	t	WEEKLY	\N	f	382	84	\N
564	2024-08-05	2024-12-12	16:50:00	18:30:00	FRIDAY	t	WEEKLY	\N	f	383	80	\N
565	2024-08-05	2024-12-12	16:50:00	18:30:00	FRIDAY	t	WEEKLY	\N	f	384	79	\N
566	2024-08-05	2024-12-11	09:20:00	11:00:00	MONDAY	t	WEEKLY	\N	f	385	87	\N
574	2024-08-05	2024-12-11	15:00:00	16:40:00	TUESDAY	t	WEEKLY	\N	f	393	87	\N
571	2024-08-05	2024-12-11	10:10:00	12:50:00	WEDNESDAY	t	WEEKLY	\N	f	390	87	\N
567	2024-08-05	2024-12-11	09:20:00	11:00:00	TUESDAY	t	WEEKLY	\N	f	386	87	\N
573	2024-08-05	2024-12-11	15:00:00	16:40:00	THURSDAY	t	WEEKLY	\N	f	392	87	\N
572	2024-08-05	2024-12-11	13:10:00	14:50:00	THURSDAY	t	WEEKLY	\N	f	391	87	\N
569	2024-08-05	2024-12-12	10:10:00	12:00:00	FRIDAY	t	WEEKLY	\N	f	388	87	\N
568	2024-08-05	2024-12-12	08:20:00	10:10:00	FRIDAY	t	WEEKLY	\N	f	387	87	\N
577	2024-08-05	2024-12-11	14:00:00	15:50:00	MONDAY	t	WEEKLY	\N	f	395	87	\N
578	2024-08-05	2024-12-11	11:10:00	12:50:00	TUESDAY	t	WEEKLY	\N	f	395	87	\N
575	2024-08-05	2024-12-12	13:10:00	14:50:00	TUESDAY	t	WEEKLY	\N	f	394	87	\N
576	2024-08-05	2024-12-12	13:10:00	14:50:00	WEDNESDAY	t	WEEKLY	\N	f	394	87	\N
596	2024-08-05	2024-12-12	07:30:00	11:00:00	FRIDAY	t	WEEKLY	\N	f	412	89	\N
600	2024-08-05	2024-12-11	09:20:00	11:00:00	WEDNESDAY	t	WEEKLY	\N	f	415	90	\N
601	2024-08-05	2024-12-11	13:10:00	14:50:00	WEDNESDAY	t	WEEKLY	\N	f	416	90	\N
602	2024-08-05	2024-12-11	14:00:00	17:40:00	MONDAY	t	WEEKLY	\N	f	417	90	\N
603	2024-08-05	2024-12-11	07:30:00	09:10:00	MONDAY	t	WEEKLY	\N	f	418	91	\N
611	2024-08-05	2024-12-12	15:00:00	16:40:00	WEDNESDAY	t	WEEKLY	\N	f	425	91	\N
608	2024-08-05	2024-12-12	08:20:00	10:10:00	WEDNESDAY	t	WEEKLY	\N	f	422	91	\N
610	2024-08-05	2024-12-12	13:10:00	14:50:00	WEDNESDAY	t	WEEKLY	\N	f	424	91	\N
605	2024-08-05	2024-12-12	13:10:00	14:50:00	TUESDAY	t	WEEKLY	\N	f	420	91	\N
609	2024-08-05	2024-12-12	10:10:00	12:00:00	WEDNESDAY	t	WEEKLY	\N	f	423	91	\N
604	2024-08-05	2024-12-12	13:10:00	15:50:00	MONDAY	t	WEEKLY	\N	f	419	91	\N
606	2024-08-05	2024-12-12	15:00:00	16:40:00	TUESDAY	t	WEEKLY	\N	f	421	91	\N
607	2024-08-05	2024-12-12	13:10:00	14:50:00	THURSDAY	t	WEEKLY	\N	f	421	91	\N
570	2024-08-05	2024-12-12	10:10:00	12:00:00	THURSDAY	t	WEEKLY	\N	f	389	87	\N
622	2024-08-05	2024-12-12	09:20:00	11:00:00	MONDAY	f	WEEKLY	\N	f	434	\N	\N
623	2024-08-05	2024-12-12	09:20:00	11:00:00	THURSDAY	f	WEEKLY	\N	f	434	\N	\N
643	2024-08-05	2024-12-12	09:20:00	11:00:00	MONDAY	f	WEEKLY	\N	f	454	\N	\N
\.


--
-- TOC entry 3204 (class 0 OID 24987)
-- Dependencies: 208
-- Data for Name: subject; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.subject (id, name, code, professors, type, class_credit, work_credit, activation, deactivation) FROM stdin;
1	Energia, Meio Ambiente e Sustentabilidade	PEA3100	{"Juan Carlos Cebrian Amasifen"}	BIANNUAL	0	0	2024-08-05	2024-12-12
2	Eletricidade Geral II	PEA3201	{"Carlos Frederico Meschini Almeida","Josemir Coelho Santos","Silvio Giuseppe Di Santo"}	BIANNUAL	0	0	2024-08-05	2024-12-12
3	Eletricidade I	PEA3288	{"Maurício Barbosa de Camargo Salles"}	BIANNUAL	0	0	2024-08-05	2024-12-12
4	Eletrotécnica Aplicada I	PEA3290	{"Silvio Giuseppe Di Santo"}	BIANNUAL	0	0	2024-08-05	2024-12-12
5	Eletricidade Geral I	PEA3294	{"(R) Milana Lima dos Santos","Carlos Frederico Meschini Almeida"}	BIANNUAL	0	0	2024-05-06	2024-08-16
6	Eletrotécnica Geral	PEA3346	{"(R) Josemir Coelho Santos"}	BIANNUAL	0	0	2024-08-05	2024-12-12
7	Laboratório de Eletricidade Geral II	PEA3389	{"Milana Lima dos Santos","Renato Machado Monaro"}	BIANNUAL	0	0	2024-08-05	2024-12-12
8	Eletricidade Aplicada I	PEA3390	{"(R) Giovanni Manassero Junior"}	BIANNUAL	0	0	2024-08-05	2024-12-12
9	Eletricidade Geral III	PEA3392	{"(R) Milana Lima dos Santos","Carlos Eduardo de Morais Pereira"}	BIANNUAL	0	0	2024-08-05	2024-12-12
10	Laboratório de Eletricidade Geral I	PEA3393	{"Maurício Barbosa de Camargo Salles","Sérgio Luiz Pereira"}	BIANNUAL	0	0	2024-08-05	2024-12-12
11	Laboratório de Máquinas Elétricas	PEA3405	{"(R) Silvio Ikuyo Nabeta"}	BIANNUAL	0	0	2024-08-05	2024-12-12
12	Laboratório de Sistemas  de Potência	PEA3406	{"Carlos Frederico Meschini Almeida"}	BIANNUAL	0	0	2024-08-05	2024-12-12
13	Máquinas Elétricas II	PEA3414	{"(R) Ivan Eduardo Chabu"}	BIANNUAL	0	0	2024-08-05	2024-12-12
14	Sistemas de Potência II	PEA3417	{"(R) Nelson Kagan"}	BIANNUAL	0	0	2024-08-05	2024-12-12
15	Laboratório de Automação de Sistemas Industriais	PEA3418	{"(R) Eduardo Lorenzetti Pellini","(R) Milana Lima dos Santos"}	BIANNUAL	0	0	2024-08-05	2024-12-12
16	Proteção e Automação de Sistemas Elétricos de Potência II	PEA3424	{"(R) Giovanni Manassero Junior"}	BIANNUAL	0	0	2024-08-05	2024-12-12
17	Laboratório de Energia	PEA3430	{"(R) Jose Aquiles Baesso Grimoni","André Luiz Veiga Gimenes"}	BIANNUAL	0	0	2024-08-05	2024-12-12
18	Uso da Energia Elétrica	PEA3440	{"(R) André Luiz Veiga Gimenes"}	BIANNUAL	0	0	2024-08-05	2024-12-12
19	Eletrônica de Potência II	PEA3490	{"(R) Lourenço Matakas Junior","(R) Wilson Komatsu"}	BIANNUAL	0	0	2024-08-05	2024-12-12
20	Projeto de Formatura I	PEA3500	{"(R) Lourenço Matakas Junior"}	BIANNUAL	0	0	2024-08-05	2024-12-12
21	Projeto de Formatura II	PEA3507	{"(R) Dorel Soares Ramos","(R) Giovanni Manassero Junior","(R) Silvio Giuseppe Di Santo","Luiz Claudio Ribeiro Galvão","Marco Antonio Saidel"}	BIANNUAL	0	0	2024-08-05	2024-12-12
22	Laboratório de Automação e Proteção de Sistemas Elétricos	PEA3524	{"(R) Milana Lima dos Santos"}	BIANNUAL	0	0	2024-08-05	2024-12-12
23	Acionamentos Elétricos Industriais	PEA3550	{"(R) Ivan Eduardo Chabu"}	BIANNUAL	0	0	2024-08-05	2024-12-12
24	Estágio Supervisionado	PEA3600	{"(R) Wilson Komatsu"}	BIANNUAL	0	0	2024-08-05	2024-12-12
25	Eletromagnetismo	PTC3213	{"(R) Luiz Cezar Trintinalia","(R) Luiz Lebensztajn","Murilo Hiroaki Seko"}	BIANNUAL	0	0	2024-08-05	2024-12-12
26	Ondas e Linhas	PTC3314	{"(R) Luiz Cezar Trintinalia","Juan Luis Poletti Soto","Renata Valeri de Freitas"}	BIANNUAL	0	0	2024-08-05	2024-12-12
27	Introdução a Redes e Comunicações	PTC3360	{"","(R) Cristiano Magalhaes Panazio","(R) Marcio Eisencraft"}	BIANNUAL	0	0	2024-08-05	2024-12-12
28	Introdução ao Processamento Digital de Sinais	PTC3361	{"","Henrique Takachi Moriya","Renata Valeri de Freitas"}	BIANNUAL	0	0	2024-08-05	2024-12-12
29	Laboratório de Circuitos de Comunicações	PTC3429	{"Murilo Hiroaki Seko"}	BIANNUAL	0	0	2024-08-05	2024-12-12
30	Sistemas de Comunicação	PTC3449	{"(R) Phillip Mark Seymour Burt"}	BIANNUAL	0	0	2024-08-05	2024-12-12
31	Processamento Estatístico e Adaptativo	PTC3451	{"(R) Maria das Dores dos Santos Miranda"}	BIANNUAL	0	0	2024-08-05	2024-12-12
32	Teoria da Informação e Codificação	PTC3452	{"(R) Guido Stolfi","(R) Paul Jean Etienne Jeszensky"}	BIANNUAL	0	0	2024-08-05	2024-12-12
33	Estágio Supervisionado	PTC3502	{"Cristiano Magalhaes Panazio"}	BIANNUAL	0	0	2024-08-05	2024-12-12
34	Projeto de Formatura em Telecomunicações	PTC3528	{"Cristiano Magalhaes Panazio","Juan Luis Poletti Soto","Phillip Mark Seymour Burt"}	BIANNUAL	0	0	2024-08-05	2024-12-12
35	Laboratório de Processamento Digital de Sinais	PTC3546	{"(R) Phillip Mark Seymour Burt"}	BIANNUAL	0	0	2024-08-05	2024-12-12
36	Detecção e Estimação de Sinais	0323150	{""}	BIANNUAL	0	0	2024-08-05	2024-12-12
37	Sistemas de Controle	PTC3020	{"(R) Fuad Kassab Junior"}	BIANNUAL	0	0	2024-05-06	2024-08-16
38	Engenho e Arte do Controle Automático	PTC3101	{""}	BIANNUAL	0	0	2024-08-05	2024-12-12
39	Laboratório de Controle	PTC3312	{"(R) Ricardo Paulino Marques","Diego Colón","Fabio de Oliveira Fialho","Felipe Miguel Pait","Fuad Kassab Junior"}	BIANNUAL	0	0	2024-08-05	2024-12-12
40	Sistemas de Controle	PTC3313	{"Diego Colón","Fuad Kassab Junior","Átila Madureira Bueno"}	BIANNUAL	0	0	2024-08-05	2024-12-12
41	Controle de Processos Industriais	PTC3414	{"(R) Claudio Garcia"}	BIANNUAL	0	0	2024-08-05	2024-12-12
42	Controle Não Linear	PTC3417	{"Felipe Miguel Pait"}	BIANNUAL	0	0	2024-08-05	2024-12-12
43	Programação Matemática Aplicada a Controle	PTC3420	{"(R) Oswaldo Luiz do Valle Costa"}	BIANNUAL	0	0	2024-08-05	2024-12-12
44	Instrumentação Industrial	PTC3421	{"(R) Ricardo Paulino Marques"}	BIANNUAL	0	0	2024-08-05	2024-12-12
45	Introdução ao Projeto de Sistemas de Controle Robustos	PTC3470	{"(R) José Jaime da Cruz"}	BIANNUAL	0	0	2024-08-05	2024-12-12
46	Práticas de Projeto de Sistemas de Controle	PTC3471	{"(R) Bruno Augusto Angelico"}	BIANNUAL	0	0	2024-08-05	2024-12-12
47	Estágio Supervisionado	PTC3501	{"Diego Colón"}	BIANNUAL	0	0	2024-08-05	2024-12-12
48	Laboratório de Projeto de Automação e Controle I	PTC3530	{"(R) Fuad Kassab Junior","Claudio Garcia","Felipe Miguel Pait"}	BIANNUAL	0	0	2024-08-05	2024-12-12
94	Redes de Computadores II	PCS3724	{"(R) Regina Melo Silveira","(R) Tereza Cristina Melo de Brito Carvalho"}	BIANNUAL	0	0	2024-05-06	2024-08-16
49	Laboratório de Projeto de Automação e Controle II	PTC3531	{"(R) Fuad Kassab Junior","Claudio Garcia","Felipe Miguel Pait"}	BIANNUAL	0	0	2024-08-05	2024-12-12
50	Ciência dos Dados em Automação e Engenharia	PTC3567	{"(R) Felipe Miguel Pait","(R) Fuad Kassab Junior","(R) Pedro Luiz Pizzigatti Corrêa"}	BIANNUAL	0	0	2024-08-05	2024-12-12
51	Dinâmica e Controle em Tempo Discreto	PTC3572	{"(R) Luiz Henrique Alves Monteiro"}	BIANNUAL	0	0	2024-08-05	2024-12-12
52	Engenharia Clínica	PTC3570	{"(R) Henrique Takachi Moriya"}	BIANNUAL	0	0	2024-08-05	2024-12-12
53	Eletrônica	PSI3024	{"(R) Sebastião Gomes dos Santos Filho","Armando Antonio Maria Lagana"}	BIANNUAL	0	0	2024-08-05	2024-12-12
54	Circuitos Elétricos I	PSI3211	{"João Francisco Justo Filho"}	BIANNUAL	0	0	2024-08-05	2024-12-12
55	Circuitos Elétricos II	PSI3213	{"(R) Flávio Almeida de Magalhães Cipparrone","(R) Magno Teófilo Madeira da Silva","Elisabete Galeazzo","Miguel Arjona Ramirez","Wagner Luiz Zucchi"}	BIANNUAL	0	0	2024-08-05	2024-12-12
56	Fundamentos de Circuitos Eletrônicos Digitais e Analógicos	PSI3262	{"(R) Antonio Carlos Seabra","(R) Magno Teófilo Madeira da Silva"}	BIANNUAL	0	0	2024-08-05	2024-12-12
57	Eletrônica I	PSI3321	{"(R) Sebastião Gomes dos Santos Filho"}	BIANNUAL	0	0	2024-08-05	2024-12-12
58	Eletrônica II	PSI3322	{"(R) Antonio Carlos Seabra","(R) João Antonio Martino"}	BIANNUAL	0	0	2024-08-05	2024-12-12
59	Laboratório de Sistemas Eletrônicos	PSI3422	{"(R) Gustavo Pamplona Rehder","(R) Hae Yong Kim"}	BIANNUAL	0	0	2024-08-05	2024-12-12
60	Processamento de Áudio e Imagem	PSI3432	{"(R) Vitor Heloiz Nascimento"}	BIANNUAL	0	0	2024-08-05	2024-12-12
62	Projeto de Sistemas Embarcados	PSI3442	{"Marcelo Knorich Zuffo"}	BIANNUAL	0	0	2024-08-05	2024-12-12
63	Projeto de Circuitos Integrados Digitais e Analógicos	PSI3452	{"(R) Ariana Maria da Conceição Lacorte Caniato Serrano","Bruno Cavalcante de Souza Sanches"}	BIANNUAL	0	0	2024-08-05	2024-12-12
64	Sensores: da Automação Industrial à IoT	PSI3464	{"(R) Fernando Josepetti Fonseca"}	BIANNUAL	0	0	2024-08-05	2024-12-12
65	Inovação em Engenharia	PSI3465	{"(R) Fernando Josepetti Fonseca","(R) Leopoldo Rideki Yoshioka"}	BIANNUAL	0	0	2024-08-05	2024-12-12
66	Concepção e Implementação de Sistemas Eletrônicos Inteligentes	PSI3472	{"(R) Hae Yong Kim","(R) Marcio Lobo Netto"}	BIANNUAL	0	0	2024-08-05	2024-12-12
67	Antenas, Micro-ondas e Óptica Moderna	PSI3482	{"(R) Ariana Maria da Conceição Lacorte Caniato Serrano","(R) Wagner Luiz Zucchi"}	BIANNUAL	0	0	2024-08-05	2024-12-12
68	Ondas Eletromagnéticas em Meios Guiados	PSI3483	{"(R) Fatima Salete Correra"}	BIANNUAL	0	0	2024-08-05	2024-12-12
69	Processamento de Voz e Aprendizagem de Máquina	PSI3501	{"(R) Miguel Arjona Ramirez"}	BIANNUAL	0	0	2024-08-05	2024-12-12
70	Realidade Virtual	PSI3502	{"(R) Marcelo Knorich Zuffo","(R) Roseli de Deus Lopes"}	BIANNUAL	0	0	2024-08-05	2024-12-12
71	Sistemas Embarcados para IoT	PSI3542	{"(R) Sergio Takeo Kofuji"}	BIANNUAL	0	0	2024-08-05	2024-12-12
72	Computação Visual	PSI3572	{"(R) Marcio Lobo Netto"}	BIANNUAL	0	0	2024-08-05	2024-12-12
73	Projeto de Formatura II	PSI3592	{"(R) Antonio Carlos Seabra","(R) Marcelo Knorich Zuffo","Roseli de Deus Lopes"}	BIANNUAL	0	0	2024-08-05	2024-12-12
74	Estágio Supervisionado	PSI3593	{"(R) Fernando Josepetti Fonseca","(R) Sergio Takeo Kofuji","Ariana Maria da Conceição Lacorte Caniato Serrano"}	BIANNUAL	0	0	2024-08-05	2024-12-12
75	Introdução à Engenharia Elétrica	0323100	{""}	BIANNUAL	0	0	2024-08-05	2024-12-12
76	Laboratório de Fabricação de Circuitos Integrados	PSI3463	{"(R) João Antonio Martino","(R) Marcelo Nelson Paez Carreno"}	BIANNUAL	0	0	2024-08-05	2024-12-12
77	Linguagem Computacional	PCS3021	{"(R) Ricardo Nakamura","(R) Romero Tori"}	BIANNUAL	0	0	2024-08-05	2024-12-12
78	Algoritmos e Estruturas de Dados para Engenharia Elétrica	PCS3110	{"(R) Anarosa Alves Franco Brandão","(R) Anna Helena Reali Costa","(R) Artur Jordão Lima Correia"}	BIANNUAL	0	0	2024-08-05	2024-12-12
79	Laboratório de Programação Orientada a Objetos para Engenharia Elétrica	PCS3111	{"(R) Fabio Levy Siqueira","(R) Kechi Hirama","(R) Pedro Luiz Pizzigatti Corrêa","(R) Solange Nice Alves de Souza","Anarosa Alves Franco Brandão","Artur Jordão Lima Correia","Ricardo Nakamura"}	BIANNUAL	0	0	2024-08-05	2024-12-12
80	Sistemas Digitais I	PCS3115	{"(R) Bruno de Carvalho Albertini","(R) Edson Satoshi Gomi"}	BIANNUAL	0	0	2024-08-05	2024-12-12
81	Engenharia de Software	PCS3213	{"(R) Jorge Luis Risco Becerra","(R) Selma Shin Shimizu Melnikoff"}	BIANNUAL	0	0	2024-08-05	2024-12-12
82	Sistemas Digitais II	PCS3225	{"","(R) Glauber De Bona","(R) Marco Tulio Carvalho de Andrade","Bruno Abrantes Basseto"}	BIANNUAL	0	0	2024-08-05	2024-12-12
83	Design e Programação de Games	PCS3549	{"(R) Ricardo Nakamura"}	BIANNUAL	0	0	2024-08-05	2024-12-12
84	Laboratório de Sistemas Embarcados	PCS3558	{"(R) Carlos Eduardo Cugnasca","Moacyr Martucci Junior"}	BIANNUAL	0	0	2024-08-05	2024-12-12
85	Tecnologias para Aplicações Interativas	PCS3559	{""}	BIANNUAL	0	0	2024-08-05	2024-12-12
86	Projeto de Formatura II	PCS3560	{"(R) João Batista Camargo Júnior","(R) Paulo Sergio Cugnasca"}	BIANNUAL	0	0	2024-08-05	2024-12-12
87	Estágio Superivisionado I	PCS3567	{"(R) Jorge Luis Risco Becerra"}	BIANNUAL	0	0	2024-08-05	2024-12-12
89	Sistemas de Computação de Alto Desempenho	PCS3568	{"(R) Liria Matsumoto Sato"}	BIANNUAL	0	0	2024-08-05	2024-12-12
90	Sistemas de Informação para Engenharia	PCS3569	{"(R) Pedro Luiz Pizzigatti Corrêa"}	BIANNUAL	0	0	2024-08-05	2024-12-12
91	Sistemas Tolerantes a Falhas	PCS3578	{"(R) João Batista Camargo Júnior"}	BIANNUAL	0	0	2024-08-05	2024-12-12
92	Aspectos Legais em Tecnologia da Informação	PCS3589	{"(R) Edson Satoshi Gomi"}	BIANNUAL	0	0	2024-08-05	2024-12-12
93	Organização e Arquitetura de Computadores II	PCS3722	{"(R) Cíntia Borges Margi","(R) Wilson Vicente Ruggiero"}	BIANNUAL	0	0	2024-05-06	2024-08-16
95	Inovação, Tecnologia, Estratégia de Negócio e a Sociedade	PCS3579	{"Regina Melo Silveira"}	BIANNUAL	0	0	2024-08-05	2024-12-12
96	Princípios de Desenvolvimento de Algoritmos	MAC0122	{"Carlos Hitoshi Morimoto","Cristina Gomes Fernandes","Fábio Happ Botler","Manoel Marcilio Sanches"}	BIANNUAL	0	0	2024-08-05	2024-12-12
97	Termodinâmica Aplicada	PME3344	{"(R) Alberto Hernandez Neto","Flávio Augusto Sanzovo Fiorelli","Jurandir Itizo Yanagihara","Maurício Silva Ferreira"}	BIANNUAL	0	0	2024-08-05	2024-12-12
98	Estatística	PRO3200	{"Alberto Wunderler Ramos","Daniel de Oliveira Mota","Jose Joaquim do Amaral Ferreira","Miguel Angelo de Carvalho Michalski","Regina Meyer Branski","Renan Favarão da Silva"}	BIANNUAL	0	0	2024-08-05	2024-12-12
99	Fundamentos de Administração	PRO3811	{"João Amato Neto","Paulino Graciano Francischini"}	BIANNUAL	0	0	2024-08-05	2024-12-12
100	Fundamentos de Economia	PRO3821	{"(R) Reinaldo Pacheco da Costa","João Amato Neto","Roberta de Castro Souza Piao"}	BIANNUAL	0	0	2024-08-05	2024-12-12
101	Física II	4323102	{"Euzi Conceicao Fernandes da Silva","Luis Gregorio Godoy de Vasconcellos Dias da Silva","Renato Higa"}	BIANNUAL	0	0	2024-08-05	2024-12-12
102	Proteção e Automação de Sistemas Elétricos de Potência I	PEA3416	{"(R) Giovanni Manassero Junior"}	BIANNUAL	0	0	2024-08-05	2024-12-12
103	Cálculo Diferencial e Integral II	MAT2454	{"Alexandre Lymberopoulos","Antonio de Padua Franco Filho","Deborah Martins Raphael","Edson Vargas","Eloi Medina Galego","Glaucio Terra","Henrique Guzzo Junior","Jose Antonio Verderesi","João Fernando da Cunha Nariyoshi","Leonardo Pellegrini Rodrigues","Marcone Corrêa Pereira","Orlando Stanley Juriaans","Oscar Joao Abdounur","Wilson Albeiro Cuellar Carrera"}	BIANNUAL	0	0	2024-08-05	2024-12-12
104	Física IV	4323204	{"Andre Bohomoletz Henriques","Carla Goldman","Fernando Tadeu Caldeira Brandt","Marco Aurélio Brizzotti Andrade","Ricardo de Lima"}	BIANNUAL	0	0	2024-08-05	2024-12-12
105	Probabilidade	0303200	{""}	BIANNUAL	0	0	2024-08-05	2024-12-12
135	Transferência de Calor	PME3360	{"(R) Maurício Silva Ferreira","Marlon Sproesser Mathias"}	BIANNUAL	0	0	2024-08-05	2024-12-12
107	Cálculo Diferencial e Integral IV	MAT2456	{"Claudio Gorodski","Edson de Faria","Jaime Angulo Pava","Martha Patrícia Dussan Angulo","Ricardo dos Santos Freire Junior"}	BIANNUAL	0	0	2024-08-05	2024-12-12
108	Introdução à Mecânica dos Sólidos	PEF3202	{"(R) Rodrigo Provasi Correia","Henrique de Britto Costa"}	BIANNUAL	0	0	2024-08-05	2024-12-12
109	Mecânica I	PME3100	{"(R) Francisco José Profito","(R) Renato Maia Matarazzo Orsino","Demetrio Cornilios Zachariadis","Edilson Hiroshi Tamai","Flavio Celso Trigo","Flavius Portella Ribas Martins","Guilherme Jorge Vernizzi Lopes","Roberto Martins de Souza","Roberto Spinola Barbosa","Ronaldo Carrion","Ronaldo de Breyne Salvagni","Éverton Lins de Oliveira"}	BIANNUAL	0	0	2024-08-05	2024-12-12
110	Mecânica dos Sólidos II	PME3211	{"(R) Clovis de Arruda Martins","(R) Roberto Ramos Junior"}	BIANNUAL	0	0	2024-08-05	2024-12-12
111	Fundamentos de Ciência e Engenharia dos Materiais	PMT3100	{"Andre Luiz da Silva","Antonio Carlos Vieira Coelho","Eduardo Franco de Monlevade","Elizabeth Grillo Fernandes"}	BIANNUAL	0	0	2024-08-05	2024-12-12
112	Introdução à Ciência dos Materiais para Engenharia	PMT3110	{"Andre Luiz da Silva","Elizabeth Grillo Fernandes","Fernando Jose Gomes Landgraf","Patrícia Schmid Calvão","Wang Shu Hui"}	BIANNUAL	0	0	2024-08-05	2024-12-12
113	Ciência dos Materiais	PMT3200	{"","Eduardo Franco de Monlevade","Ticiane Sanches Valera"}	BIANNUAL	0	0	2024-08-05	2024-12-12
114	Conservação de Massa e Energia	PQI3103	{"(R) Antonio Carlos Silva Costa Teixeira","Denise Crocce Romano Espinosa","Jorge Alberto Soares Tenório"}	BIANNUAL	0	0	2024-08-05	2024-12-11
115	Fenômenos de Transporte I	PQI3202	{"","(R) José Luis Pires Camacho","Ardson dos Santos Vianna Junior","José Luis de Paiva","Martina Costa Reis"}	BIANNUAL	0	0	2024-08-05	2024-12-11
116	Álgebra Linear II	MAT3458	{"","Alexandre Lymberopoulos","Daniel Victor Tausk","Javier Sanchez Serdà","Kostiantyn Iusenko","Valentin Raphael Henri Ferenczi","Vitor de Oliveira Ferreira"}	BIANNUAL	0	0	2024-08-05	2024-12-12
106	Física I	4323101	{"Não informado"}	BIANNUAL	3	0	2014-01-01	\N
117	Projeto de Formatura I	PSI3591	{"(R) Antonio Carlos Seabra","(R) Marcelo Knorich Zuffo","Roseli de Deus Lopes"}	BIANNUAL	0	0	2024-08-05	2024-12-12
118	Conversão Eletromecânica de Energia	PEA3399	{"Daniel Ribeiro Gomes"}	BIANNUAL	0	0	2024-09-02	2024-12-13
123	Práticas de Oficina para Engenharia Mecânica	PME3110	{"(R) Marcelo Augusto Leal Alves"}	BIANNUAL	0	0	2024-08-05	2024-12-12
124	Expressão Gráfica em Engenharia Mecânica	PME3120	{"(R) Marcelo Augusto Leal Alves","Francisco José Profito","Juliane Ribeiro da Cruz Alves"}	BIANNUAL	0	0	2024-08-05	2024-12-12
125	Laboratório de Simulações Numéricas	PME3201	{"(R) Flavius Portella Ribas Martins","Walter Jorge Augusto Ponge Ferreira"}	BIANNUAL	0	0	2024-08-05	2024-12-12
127	Transferência de Calor e Massa	PME3361	{"","(R) José Roberto Simões Moreira","Arlindo Tribess","Ernani Vitillo Volpe","Guenther Carlos Krieger Filho"}	BIANNUAL	0	0	2024-08-05	2024-12-12
128	Mecânica dos Fluidos I	PME3230	{"","(R) Antonio Luis de Campos Mariani","Alberto Hernandez Neto","Ali Allahyarzadeh Bidgoli","Bruno Souza Carmo","Fernando Luiz Sacomano Filho","Humberto de Camargo Gissoni","Jayme Pinto Ortiz","Marcos Tadeu Pereira"}	BIANNUAL	0	0	2024-08-05	2024-12-12
129	Noções e Desenho Técnico de Instalações Industriais	PME0464	{"(R) Marcelo Augusto Leal Alves"}	BIANNUAL	0	0	2024-08-05	2024-12-12
130	Mecânica dos Fluidos : Noções, Laboratório e Aplicações	PME3332	{"(R) Jorge Luis Baliño"}	BIANNUAL	0	0	2024-08-05	2024-12-12
131	Termodinâmica II	PME3341	{"(R) Silvio de Oliveira Junior"}	BIANNUAL	0	0	2024-08-05	2024-12-12
132	Elementos de Máquinas I	PME3350	{"(R) Marcelo Augusto Leal Alves"}	BIANNUAL	0	0	2024-08-05	2024-12-12
136	Modelagem de Sistemas Dinâmicos	PME3380	{"Flavio Celso Trigo","Renato Maia Matarazzo Orsino"}	BIANNUAL	0	0	2024-08-05	2024-12-12
137	Laboratório de Medição e Controle Discreto	PME3402	{"(R) Edilson Hiroshi Tamai","(R) Flavio Celso Trigo"}	BIANNUAL	0	0	2024-08-05	2024-12-12
138	Laboratório de  Vibrações e  Controle	PME3403	{"(R) Roberto Spinola Barbosa","(R) Walter Jorge Augusto Ponge Ferreira","Francisco Emilio Baccaro Nigro"}	BIANNUAL	0	0	2024-08-05	2024-12-12
139	Seleção de Materiais para Engenharia Mecânica	PME3431	{"(R) Roberto Martins de Souza","Juliane Ribeiro da Cruz Alves"}	BIANNUAL	0	0	2024-08-05	2024-12-12
140	Projeto de Máquinas	PME3472	{"(R) Marcelo Augusto Leal Alves"}	BIANNUAL	0	0	2024-08-05	2024-12-12
141	Sistemas Térmicos	PME3479	{"(R) Arlindo Tribess","(R) Flávio Augusto Sanzovo Fiorelli","(R) Jurandir Itizo Yanagihara","Fernando Luiz Sacomano Filho"}	BIANNUAL	0	0	2024-08-05	2024-12-12
142	Motores de Combustão Interna	PME3480	{"(R) Guenther Carlos Krieger Filho"}	BIANNUAL	0	0	2024-08-05	2024-12-12
143	Controle Discreto	PME3482	{"(R) Raúl González Lima"}	BIANNUAL	0	0	2024-08-05	2024-12-12
144	Estágio Supervisionado	PME3597	{"(R) Paulo Carlos Kaminski"}	BIANNUAL	0	0	2024-08-05	2024-12-12
145	Introdução ao Projeto Integrado	PME3598	{"(R) Alberto Hernandez Neto"}	BIANNUAL	0	0	2024-08-05	2024-12-12
146	Projeto Integrado II	PME3600	{"(R) Alberto Hernandez Neto"}	BIANNUAL	0	0	2024-08-05	2024-12-12
147	Introdução às Estruturas Aeronáuticas	PME3554	{"(R) Roberto Ramos Junior"}	BIANNUAL	0	0	2024-08-05	2024-12-12
148	Dinâmica dos Fluidos Computacional	PME3556	{"(R) Fábio Saltara"}	BIANNUAL	0	0	2024-08-05	2024-12-12
149	Projeto Aerodinâmico de Aeronaves	PME3559	{"Marlon Sproesser Mathias"}	BIANNUAL	0	0	2024-08-05	2024-12-12
150	Engenharia Automotiva II	PME3541	{"Marcelo Augusto Leal Alves"}	BIANNUAL	0	0	2024-08-05	2024-12-12
154	Técnicas Experimentais e Computacionais em Biomecânica e Sistemas Vasculares	PME3534	{"(R) Raúl González Lima"}	BIANNUAL	0	0	2024-08-05	2024-12-12
155	Tecnologia e Desenvolvimento Social II	0303603	{"(R) Antonio Luis de Campos Mariani","Marlon Sproesser Mathias"}	BIANNUAL	0	0	2024-08-05	2024-12-12
151	Estruturas Mecânicas e de Veículos	PME3543	{"(R) Leandro Vieira da Silva Macedo"}	BIANNUAL	0	0	2024-08-05	2024-12-12
156	Princípios de Células a Combustível	PME3560	{"(R) Julio Romano Meneghini"}	BIANNUAL	0	0	2024-08-05	2024-12-12
152	Engenharia de Energia Eólica	PME3562	{"(R) Bruno Souza Carmo","(R) Demetrio Cornilios Zachariadis"}	BIANNUAL	0	0	2024-08-05	2024-12-12
157	Atividades Especiais em Engenharia II	PME3596	{"(R) Antonio Luis de Campos Mariani","(R) Marcelo Augusto Leal Alves"}	BIANNUAL	0	0	2024-08-05	2024-12-12
164	Planejamento de Lavra de Minas	PMI3220	{"(R) Giorgio Francesco Cesare de Tomi","(R) Ricardo Cabral de Azevedo"}	BIANNUAL	0	0	2024-08-05	2024-12-11
165	Introdução à Engenharia de Petróleo	PMI3302	{"(R) Eduardo Cesar Sansone"}	BIANNUAL	0	0	2024-08-05	2024-12-11
166	Gerenciamento de Risco de Segurança	PMI3226	{"(R) Anna Luiza Marques Ayres da Silva","Ana Carolina Russo"}	BIANNUAL	0	0	2024-08-05	2024-12-11
167	Engenharia de Saúde Ocupacional: Agentes Físicos e Químicos	PMI3219	{"(R) Anna Luiza Marques Ayres da Silva","Ana Carolina Russo"}	BIANNUAL	0	0	2024-08-05	2024-12-11
153	Laboratório de Energias Renováveis	PME3563	{"(R) José Roberto Simões Moreira","André Luiz Veiga Gimenes","Jose Aquiles Baesso Grimoni"}	BIANNUAL	0	0	2024-08-05	2024-12-12
159	Ventilação de Minas, Túneis e Usinas	PMI3221	{"(R) Anna Luiza Marques Ayres da Silva"}	BIANNUAL	0	0	2024-08-05	2024-12-11
160	Legislação e Política Mineral	PMI3225	{"(R) Luis Enrique Sánchez","(R) Manoel Rodrigues Neves"}	BIANNUAL	0	0	2024-08-05	2024-12-11
161	Técnicas de Otimização em Engenharia de Petróleo	PMI3917	{"(R) Elsa Vásquez Alvarez"}	BIANNUAL	0	0	2024-08-05	2024-12-12
162	Trabalho de Conclusão de Curso II	PMI3349	{"(R) Cleyton de Carvalho Carneiro","(R) Rafael dos Santos Gioria"}	BIANNUAL	0	0	2024-08-05	2024-12-12
163	Geometria Gráfica para Engenharia	PCC3101	{"Elsa Vásquez Alvarez"}	BIANNUAL	0	0	2024-08-05	2024-12-12
168	Ciência de Dados para Engenharia de Petróleo	PMI3930	{"Rafael dos Santos Gioria"}	BIANNUAL	0	0	2024-08-05	2024-12-12
169	Tratamento de Minérios: Concentração por Flotação	PMI3222	{"(R) Laurindo de Salles Leal Filho"}	BIANNUAL	0	0	2024-08-05	2024-12-11
170	Manuseio de Sólidos Granulados em Suspensão na Mineração	PMI3805	{"(R) Jose Renato Baptista de Lima","Arthur Pinto Chaves"}	BIANNUAL	0	0	2024-08-05	2024-12-11
171	Projeto de Lavra de Mina	PMI3236	{"(R) Giorgio Francesco Cesare de Tomi","(R) Ricardo Cabral de Azevedo"}	BIANNUAL	0	0	2024-08-05	2024-12-11
172	Projeto de Usina de Tratamento de Minérios	PMI3240	{"(R) Maurício Guimarães Bergerman"}	BIANNUAL	0	0	2024-08-05	2024-12-11
173	Geomecânica Aplicada à Engenharia de Petróleo	PMI3304	{"(R) Eduardo Cesar Sansone"}	BIANNUAL	0	0	2024-08-05	2024-12-12
174	Controle da Poluição em Operações de Lavra a Céu Aberto	PMI3235	{"(R) Wilson Siguemasa Iramina"}	BIANNUAL	0	0	2024-08-05	2024-12-11
175	Trabalho de Conclusão de Curso  em Engenharia de Minas II	PMI3228	{"(R) Luis Enrique Sánchez"}	BIANNUAL	0	0	2024-08-05	2024-12-11
176	Viabilidade Econômica de Projetos Avançada	PMI3238	{"(R) Manoel Rodrigues Neves"}	BIANNUAL	0	0	2024-08-05	2024-12-11
177	Introdução às Ciências Ambientais Aplicada à Engenharia de Petróleo	PMI3334	{"(R) Patricia Helena Lara dos Santos Matai"}	BIANNUAL	0	0	2024-08-05	2024-12-12
178	Tópicos Especiais de Química Aplicados à Engenharia de Petróleo	PMI3315	{"(R) Patricia Helena Lara dos Santos Matai"}	BIANNUAL	0	0	2024-08-05	2024-12-12
179	Projeto de Usinas de Reciclagem de Resíduos Sólidos Industriais e de Mineração	PMI3801	{"(R) Carina Ulsen","(R) Maurício Guimarães Bergerman"}	BIANNUAL	0	0	2024-08-05	2024-12-11
180	Estágio Supervisionado em Engenharia de Minas	PMI3229	{"(R) Jose Renato Baptista de Lima"}	BIANNUAL	0	0	2024-08-05	2024-12-11
182	Avaliação de Impactos Ambientais	PMI3401	{"(R) Luis Enrique Sánchez","Juliana Siqueira Gay"}	BIANNUAL	0	0	2024-08-05	2024-12-11
183	Introdução ao Meio Ambiente e Sustentabilidade na Mineração	PMI3328	{"(R) Luis Enrique Sánchez"}	BIANNUAL	0	0	2024-08-05	2024-12-11
184	Técnicas de Caracterização de Materiais	PMI3021	{"(R) Carina Ulsen","Jean Vicente Ferrari"}	BIANNUAL	0	0	2024-08-05	2024-12-11
185	Lavra a Céu-Aberto	PMI3325	{"(R) Giorgio Francesco Cesare de Tomi"}	BIANNUAL	0	0	2024-08-05	2024-12-11
186	Laboratório de Eletrotécnica Geral	PEA3397	{"Gleison Elias da Silva"}	BIANNUAL	0	0	2024-08-05	2024-12-12
187	Britagem e Peneiramento na Indústria de Agregados para a Construção Civil	PMI3810	{"(R) Jose Renato Baptista de Lima"}	BIANNUAL	0	0	2024-08-05	2024-12-11
188	Propriedades de Fluidos do Petróleo	PQI3440	{"Nara Angélica Policarpo"}	BIANNUAL	0	0	2024-08-05	2024-12-12
189	Mecânica das Rochas Aplicada à Mineração II	PMI3309	{"(R) Eduardo Cesar Sansone"}	BIANNUAL	0	0	2024-08-05	2024-12-11
190	Perfuração e Desmonte de Rochas	PMI3321	{"(R) Eduardo Cesar Sansone","(R) Wilson Siguemasa Iramina"}	BIANNUAL	0	0	2024-08-05	2024-12-11
191	Tratamento de Minérios  Cominuição e Classificação	PMI3323	{"(R) Homero Delboni Junior"}	BIANNUAL	0	0	2024-08-05	2024-12-11
192	Amostragem e Controle de Qualidade na Mineração	PMI3231	{"(R) Ana Carolina Chieregati"}	BIANNUAL	0	0	2024-08-05	2024-12-11
193	Perfilagem de Poços	PMI3928	{"(R) Cleyton de Carvalho Carneiro"}	BIANNUAL	0	0	2024-08-05	2024-12-12
194	Completação e Estimulação de Poços	PMI3345	{"(R) Nara Angélica Policarpo"}	BIANNUAL	0	0	2024-08-05	2024-12-12
195	Projeto de Engenharia de Petróleo	PMI3348	{"(R) Nara Angélica Policarpo"}	BIANNUAL	0	0	2024-08-05	2024-12-12
196	Avaliação Econômica de Projetos de Óleo e Gás	PMI3341	{"Regina Meyer Branski"}	BIANNUAL	0	0	2024-08-05	2024-12-12
197	Projeto e Análise de Testes de Poços de Petróleo	PMI3347	{"(R) Ricardo Cabral de Azevedo"}	BIANNUAL	0	0	2024-08-05	2024-12-12
198	Engenharia de Reservatórios II	PMI3344	{"(R) Ricardo Cabral de Azevedo"}	BIANNUAL	0	0	2024-08-05	2024-12-12
199	Projeto de Poço	PMI3337	{"(R) Nara Angélica Policarpo"}	BIANNUAL	0	0	2024-08-05	2024-12-12
200	Simulação de Reservatórios de Petróleo	PMI3346	{"Rafael dos Santos Gioria"}	BIANNUAL	0	0	2024-08-05	2024-12-12
201	Visitas Supervisionadas em Engenharia de Petróleo	PMI3936	{"(R) Elsa Vásquez Alvarez"}	BIANNUAL	0	0	2024-08-05	2024-12-12
202	Fundamentos de Termodinâmica para Engenharia de Petróleo	PMI3329	{"(R) Rafael dos Santos Gioria"}	BIANNUAL	0	0	2024-08-05	2024-12-12
203	Mecânica dos Fluidos Aplicada a Reservatórios	PMI3317	{"(R) Rafael dos Santos Gioria"}	BIANNUAL	0	0	2024-08-05	2024-12-12
205	Estruturas na Arquitetura I V: Projeto	PEF2604	{"Martin Paul Schwark","Pedro Afonso de Oliveira Almeida"}	BIANNUAL	0	0	2024-08-05	2024-12-12
206	Projeto de Sistemas de Drenagem Urbana	PHA3516	{"Joaquin Ignacio Bonnecarrere Garcia"}	BIANNUAL	0	0	2024-08-05	2024-12-12
207	Química Ambiental e Fundamentos de Termodinâmica	PQI3222	{"Luis Alberto Follegatti Romero"}	BIANNUAL	0	0	2024-08-05	2024-12-11
213	Real Estate - Análise de Investimentos	PCC3412	{"(R) Claudio Tavares de Alencar","(R) Eliane Monetti"}	BIANNUAL	0	0	2024-08-05	2024-12-12
214	Materiais e Componentes, Reciclagem e Gestão de Resíduos da Construção	PCC3556	{"(R) Sérgio Cirelli Angulo"}	BIANNUAL	0	0	2024-08-05	2024-12-12
209	Física das Construções	PCC3260	{"(R) Daniel Setrak Sowmy"}	BIANNUAL	0	0	2024-08-05	2024-12-12
216	Planejamento e Controle de Obras	PCC3529	{"(R) Luiz Reynaldo de Azevedo Cardoso"}	BIANNUAL	0	0	2024-08-05	2024-12-12
210	Cidades Inteligentes	0313562	{"Marcelo Schneck de Paula Pessoa"}	BIANNUAL	0	0	2024-08-05	2024-12-12
217	Engenharia e Meio Ambiente	PHA3001	{"(R) Monica Ferreira do Amaral Porto","Arisvaldo Vieira Mello Júnior","Juliana Siqueira Gay","Rachel Biancalana Costa","Sidney Seckler Ferreira Filho"}	BIANNUAL	0	0	2024-08-05	2024-12-12
211	Projeto de Vias de Transporte	PTR3321	{"(R) Ettore Jose Bottura","(R) Felipe Issa Kabbach Junior","Laura Nascimento Mazzoni","Rosângela dos Santos Motta"}	BIANNUAL	0	0	2024-08-05	2024-12-12
212	Poluição e Qualidade da Água	PHA3360	{"(R) José Carlos Mierzwa","(R) Sidney Seckler Ferreira Filho"}	BIANNUAL	0	0	2024-08-05	2024-12-12
218	Oceanografia Física Descritiva para Engenharia Ambiental	IOF0273	{"(R) Joseph Harari"}	BIANNUAL	0	0	2024-08-05	2024-12-12
215	Engenharia Civil e o Meio Ambiente	PHA3203	{"(R) Amarilis Lucia Casteli Figueiredo Gallardo"}	BIANNUAL	0	0	2024-08-05	2024-12-12
\.


--
-- TOC entry 3223 (class 0 OID 25201)
-- Dependencies: 227
-- Data for Name: subjectbuildinglink; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.subjectbuildinglink (subject_id, building_id) FROM stdin;
1	2
2	2
3	2
4	2
5	2
6	2
7	2
8	2
9	2
10	2
11	2
12	2
13	2
14	2
15	2
16	2
17	2
18	2
19	2
20	2
21	2
22	2
23	2
24	2
25	2
26	2
27	2
28	2
29	2
30	2
31	2
32	2
33	2
34	2
35	2
36	2
37	2
38	2
39	2
40	2
41	2
42	2
43	2
44	2
45	2
46	2
47	2
48	2
49	2
50	2
51	2
52	2
53	2
54	2
55	2
56	2
57	2
58	2
59	2
60	2
62	2
63	2
64	2
65	2
66	2
67	2
68	2
69	2
70	2
71	2
72	2
73	2
74	2
75	2
76	2
77	2
78	2
79	2
80	2
81	2
82	2
83	2
84	2
85	2
86	2
87	2
89	2
90	2
91	2
92	2
93	2
94	2
95	2
96	2
97	2
98	2
99	2
100	2
101	2
102	2
103	1
104	1
105	1
106	1
107	1
108	1
109	1
110	1
111	1
112	1
113	1
114	7
115	1
116	1
117	2
118	2
123	6
124	6
125	6
127	6
128	6
129	6
130	6
131	6
132	6
135	6
136	6
137	6
138	6
139	6
140	6
141	6
142	6
143	6
144	6
145	6
146	6
147	6
148	6
149	6
150	6
151	6
152	6
153	6
154	6
155	6
156	6
157	6
159	8
160	8
161	8
162	8
163	8
164	8
165	8
166	8
167	8
168	8
169	8
170	8
171	8
172	8
173	8
174	8
175	8
176	8
177	8
178	8
179	8
180	8
182	8
183	8
184	8
185	8
186	8
187	8
188	8
189	8
190	8
191	8
192	8
193	8
194	8
195	8
196	8
197	8
198	8
199	8
200	8
201	8
202	8
203	8
205	4
206	4
207	4
209	4
210	4
211	4
212	4
213	4
214	4
215	4
216	4
217	4
218	4
\.


--
-- TOC entry 3206 (class 0 OID 24999)
-- Dependencies: 210
-- Data for Name: user; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public."user" (id, username, email, is_admin, name, cognito_id, updated_at, created_by_id) FROM stdin;
1	admin	amdmin@uspolis.com	t	admin	123	2024-07-28 19:05:03.317307	\N
2	hfduran	henriqueduran15@gmail.com	t	Henrique Duran	henriqueduran15@gmail.com	2024-07-28 19:05:03.317	\N
3	avilare	renandeluca01@gmail.com	t	Renan Ávila	renandeluca01@gmail.com	2024-07-29 01:48:38.78413	2
4	levy	levy.siqueira@usp.br	t	Fábio Levy	levy.siqueira@usp.br	2024-07-29 01:48:38.78413	2
5	fastshowdev	gabriel_camargo@usp.br	t	Gabriel Camargo	gabriel_camargo@usp.br	2024-07-29 01:48:38.78413	2
\.


--
-- TOC entry 3224 (class 0 OID 25216)
-- Dependencies: 228
-- Data for Name: userbuildinglink; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.userbuildinglink (user_id, building_id) FROM stdin;
\.


--
-- TOC entry 3256 (class 0 OID 0)
-- Dependencies: 211
-- Name: building_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.building_id_seq', 8, true);


--
-- TOC entry 3257 (class 0 OID 0)
-- Dependencies: 213
-- Name: calendar_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.calendar_id_seq', 1, true);


--
-- TOC entry 3258 (class 0 OID 0)
-- Dependencies: 215
-- Name: class_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.class_id_seq', 455, true);


--
-- TOC entry 3259 (class 0 OID 0)
-- Dependencies: 223
-- Name: classroom_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.classroom_id_seq', 93, true);


--
-- TOC entry 3260 (class 0 OID 0)
-- Dependencies: 217
-- Name: comment_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.comment_id_seq', 12, true);


--
-- TOC entry 3261 (class 0 OID 0)
-- Dependencies: 235
-- Name: forumpost_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.forumpost_id_seq', 9, true);


--
-- TOC entry 3262 (class 0 OID 0)
-- Dependencies: 225
-- Name: holiday_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.holiday_id_seq', 32, true);


--
-- TOC entry 3263 (class 0 OID 0)
-- Dependencies: 219
-- Name: holidaycategory_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.holidaycategory_id_seq', 3, true);


--
-- TOC entry 3264 (class 0 OID 0)
-- Dependencies: 203
-- Name: institutionalevent_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.institutionalevent_id_seq', 1, false);


--
-- TOC entry 3265 (class 0 OID 0)
-- Dependencies: 205
-- Name: mobileuser_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.mobileuser_id_seq', 44, true);


--
-- TOC entry 3266 (class 0 OID 0)
-- Dependencies: 233
-- Name: occurrence_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.occurrence_id_seq', 9870, true);


--
-- TOC entry 3267 (class 0 OID 0)
-- Dependencies: 229
-- Name: reservation_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.reservation_id_seq', 1, false);


--
-- TOC entry 3268 (class 0 OID 0)
-- Dependencies: 231
-- Name: schedule_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.schedule_id_seq', 645, true);


--
-- TOC entry 3269 (class 0 OID 0)
-- Dependencies: 207
-- Name: subject_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.subject_id_seq', 218, true);


--
-- TOC entry 3270 (class 0 OID 0)
-- Dependencies: 209
-- Name: user_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.user_id_seq', 5, true);


--
-- TOC entry 2985 (class 2606 OID 24954)
-- Name: alembic_version alembic_version_pkc; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.alembic_version
    ADD CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num);


--
-- TOC entry 2997 (class 2606 OID 25024)
-- Name: building building_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.building
    ADD CONSTRAINT building_pkey PRIMARY KEY (id);


--
-- TOC entry 3000 (class 2606 OID 25041)
-- Name: calendar calendar_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.calendar
    ADD CONSTRAINT calendar_pkey PRIMARY KEY (id);


--
-- TOC entry 3013 (class 2606 OID 25113)
-- Name: calendarholidaycategorylink calendarholidaycategorylink_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.calendarholidaycategorylink
    ADD CONSTRAINT calendarholidaycategorylink_pkey PRIMARY KEY (calendar_id, holiday_category_id);


--
-- TOC entry 3003 (class 2606 OID 25067)
-- Name: class class_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.class
    ADD CONSTRAINT class_pkey PRIMARY KEY (id);


--
-- TOC entry 3015 (class 2606 OID 25128)
-- Name: classcalendarlink classcalendarlink_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.classcalendarlink
    ADD CONSTRAINT classcalendarlink_pkey PRIMARY KEY (class_id, calendar_id);


--
-- TOC entry 3017 (class 2606 OID 25149)
-- Name: classroom classroom_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.classroom
    ADD CONSTRAINT classroom_pkey PRIMARY KEY (id);


--
-- TOC entry 3008 (class 2606 OID 25086)
-- Name: comment comment_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.comment
    ADD CONSTRAINT comment_pkey PRIMARY KEY (id);


--
-- TOC entry 3039 (class 2606 OID 25370)
-- Name: forumpost forumpost_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.forumpost
    ADD CONSTRAINT forumpost_pkey PRIMARY KEY (id);


--
-- TOC entry 3041 (class 2606 OID 33146)
-- Name: forumpostreportlink forumpostreportlink_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.forumpostreportlink
    ADD CONSTRAINT forumpostreportlink_pkey PRIMARY KEY (forum_post_id, mobile_user_id);


--
-- TOC entry 3021 (class 2606 OID 25190)
-- Name: holiday holiday_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.holiday
    ADD CONSTRAINT holiday_pkey PRIMARY KEY (id);


--
-- TOC entry 3010 (class 2606 OID 25102)
-- Name: holidaycategory holidaycategory_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.holidaycategory
    ADD CONSTRAINT holidaycategory_pkey PRIMARY KEY (id);


--
-- TOC entry 2987 (class 2606 OID 24965)
-- Name: institutionalevent institutionalevent_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.institutionalevent
    ADD CONSTRAINT institutionalevent_pkey PRIMARY KEY (id);


--
-- TOC entry 2989 (class 2606 OID 24976)
-- Name: mobileuser mobileuser_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.mobileuser
    ADD CONSTRAINT mobileuser_pkey PRIMARY KEY (id);


--
-- TOC entry 3037 (class 2606 OID 25335)
-- Name: occurrence occurrence_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.occurrence
    ADD CONSTRAINT occurrence_pkey PRIMARY KEY (id);


--
-- TOC entry 3030 (class 2606 OID 25251)
-- Name: reservation reservation_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.reservation
    ADD CONSTRAINT reservation_pkey PRIMARY KEY (id);


--
-- TOC entry 3034 (class 2606 OID 25312)
-- Name: schedule schedule_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.schedule
    ADD CONSTRAINT schedule_pkey PRIMARY KEY (id);


--
-- TOC entry 2992 (class 2606 OID 24995)
-- Name: subject subject_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.subject
    ADD CONSTRAINT subject_pkey PRIMARY KEY (id);


--
-- TOC entry 3025 (class 2606 OID 25205)
-- Name: subjectbuildinglink subjectbuildinglink_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.subjectbuildinglink
    ADD CONSTRAINT subjectbuildinglink_pkey PRIMARY KEY (subject_id, building_id);


--
-- TOC entry 3006 (class 2606 OID 25069)
-- Name: class unique_class_code_for_subject; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.class
    ADD CONSTRAINT unique_class_code_for_subject UNIQUE (code, subject_id);


--
-- TOC entry 3019 (class 2606 OID 25151)
-- Name: classroom unique_classroom_name_for_building; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.classroom
    ADD CONSTRAINT unique_classroom_name_for_building UNIQUE (name, building_id);


--
-- TOC entry 3023 (class 2606 OID 25352)
-- Name: holiday unique_holiday_date_for_category; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.holiday
    ADD CONSTRAINT unique_holiday_date_for_category UNIQUE (date, category_id);


--
-- TOC entry 3032 (class 2606 OID 25253)
-- Name: reservation unique_reservation_name_for_classroom; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.reservation
    ADD CONSTRAINT unique_reservation_name_for_classroom UNIQUE (name, classroom_id);


--
-- TOC entry 2995 (class 2606 OID 25007)
-- Name: user user_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."user"
    ADD CONSTRAINT user_pkey PRIMARY KEY (id);


--
-- TOC entry 3027 (class 2606 OID 25220)
-- Name: userbuildinglink userbuildinglink_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.userbuildinglink
    ADD CONSTRAINT userbuildinglink_pkey PRIMARY KEY (user_id, building_id);


--
-- TOC entry 2998 (class 1259 OID 25030)
-- Name: ix_building_name; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_building_name ON public.building USING btree (name);


--
-- TOC entry 3001 (class 1259 OID 25047)
-- Name: ix_calendar_name; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_calendar_name ON public.calendar USING btree (name);


--
-- TOC entry 3004 (class 1259 OID 25075)
-- Name: ix_class_subject_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_class_subject_id ON public.class USING btree (subject_id);


--
-- TOC entry 3011 (class 1259 OID 25108)
-- Name: ix_holidaycategory_name; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_holidaycategory_name ON public.holidaycategory USING btree (name);


--
-- TOC entry 3035 (class 1259 OID 25346)
-- Name: ix_occurrence_schedule_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_occurrence_schedule_id ON public.occurrence USING btree (schedule_id);


--
-- TOC entry 3028 (class 1259 OID 25264)
-- Name: ix_reservation_created_by_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_reservation_created_by_id ON public.reservation USING btree (created_by_id);


--
-- TOC entry 2990 (class 1259 OID 24996)
-- Name: ix_subject_code; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_subject_code ON public.subject USING btree (code);


--
-- TOC entry 2993 (class 1259 OID 25013)
-- Name: ix_user_username; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_user_username ON public."user" USING btree (username);


--
-- TOC entry 3043 (class 2606 OID 25025)
-- Name: building building_created_by_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.building
    ADD CONSTRAINT building_created_by_id_fkey FOREIGN KEY (created_by_id) REFERENCES public."user"(id);


--
-- TOC entry 3044 (class 2606 OID 25042)
-- Name: calendar calendar_created_by_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.calendar
    ADD CONSTRAINT calendar_created_by_id_fkey FOREIGN KEY (created_by_id) REFERENCES public."user"(id);


--
-- TOC entry 3048 (class 2606 OID 25114)
-- Name: calendarholidaycategorylink calendarholidaycategorylink_calendar_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.calendarholidaycategorylink
    ADD CONSTRAINT calendarholidaycategorylink_calendar_id_fkey FOREIGN KEY (calendar_id) REFERENCES public.calendar(id);


--
-- TOC entry 3049 (class 2606 OID 25119)
-- Name: calendarholidaycategorylink calendarholidaycategorylink_holiday_category_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.calendarholidaycategorylink
    ADD CONSTRAINT calendarholidaycategorylink_holiday_category_id_fkey FOREIGN KEY (holiday_category_id) REFERENCES public.holidaycategory(id);


--
-- TOC entry 3045 (class 2606 OID 25070)
-- Name: class class_subject_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.class
    ADD CONSTRAINT class_subject_id_fkey FOREIGN KEY (subject_id) REFERENCES public.subject(id);


--
-- TOC entry 3050 (class 2606 OID 25129)
-- Name: classcalendarlink classcalendarlink_calendar_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.classcalendarlink
    ADD CONSTRAINT classcalendarlink_calendar_id_fkey FOREIGN KEY (calendar_id) REFERENCES public.calendar(id);


--
-- TOC entry 3051 (class 2606 OID 25134)
-- Name: classcalendarlink classcalendarlink_class_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.classcalendarlink
    ADD CONSTRAINT classcalendarlink_class_id_fkey FOREIGN KEY (class_id) REFERENCES public.class(id);


--
-- TOC entry 3052 (class 2606 OID 25152)
-- Name: classroom classroom_building_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.classroom
    ADD CONSTRAINT classroom_building_id_fkey FOREIGN KEY (building_id) REFERENCES public.building(id);


--
-- TOC entry 3053 (class 2606 OID 25157)
-- Name: classroom classroom_created_by_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.classroom
    ADD CONSTRAINT classroom_created_by_id_fkey FOREIGN KEY (created_by_id) REFERENCES public."user"(id);


--
-- TOC entry 3046 (class 2606 OID 25087)
-- Name: comment comment_created_by_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.comment
    ADD CONSTRAINT comment_created_by_id_fkey FOREIGN KEY (created_by_id) REFERENCES public.mobileuser(id);


--
-- TOC entry 3067 (class 2606 OID 25371)
-- Name: forumpost forumpost_class_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.forumpost
    ADD CONSTRAINT forumpost_class_id_fkey FOREIGN KEY (class_id) REFERENCES public.class(id);


--
-- TOC entry 3068 (class 2606 OID 25376)
-- Name: forumpost forumpost_subject_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.forumpost
    ADD CONSTRAINT forumpost_subject_id_fkey FOREIGN KEY (subject_id) REFERENCES public.subject(id);


--
-- TOC entry 3069 (class 2606 OID 25381)
-- Name: forumpost forumpost_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.forumpost
    ADD CONSTRAINT forumpost_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.mobileuser(id);


--
-- TOC entry 3070 (class 2606 OID 33147)
-- Name: forumpostreportlink forumpostreportlink_forum_post_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.forumpostreportlink
    ADD CONSTRAINT forumpostreportlink_forum_post_id_fkey FOREIGN KEY (forum_post_id) REFERENCES public.forumpost(id);


--
-- TOC entry 3071 (class 2606 OID 33152)
-- Name: forumpostreportlink forumpostreportlink_mobile_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.forumpostreportlink
    ADD CONSTRAINT forumpostreportlink_mobile_user_id_fkey FOREIGN KEY (mobile_user_id) REFERENCES public.mobileuser(id);


--
-- TOC entry 3054 (class 2606 OID 25191)
-- Name: holiday holiday_category_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.holiday
    ADD CONSTRAINT holiday_category_id_fkey FOREIGN KEY (category_id) REFERENCES public.holidaycategory(id);


--
-- TOC entry 3055 (class 2606 OID 25196)
-- Name: holiday holiday_created_by_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.holiday
    ADD CONSTRAINT holiday_created_by_id_fkey FOREIGN KEY (created_by_id) REFERENCES public."user"(id);


--
-- TOC entry 3047 (class 2606 OID 25103)
-- Name: holidaycategory holidaycategory_created_by_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.holidaycategory
    ADD CONSTRAINT holidaycategory_created_by_id_fkey FOREIGN KEY (created_by_id) REFERENCES public."user"(id);


--
-- TOC entry 3065 (class 2606 OID 25336)
-- Name: occurrence occurrence_classroom_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.occurrence
    ADD CONSTRAINT occurrence_classroom_id_fkey FOREIGN KEY (classroom_id) REFERENCES public.classroom(id);


--
-- TOC entry 3066 (class 2606 OID 25341)
-- Name: occurrence occurrence_schedule_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.occurrence
    ADD CONSTRAINT occurrence_schedule_id_fkey FOREIGN KEY (schedule_id) REFERENCES public.schedule(id);


--
-- TOC entry 3060 (class 2606 OID 25254)
-- Name: reservation reservation_classroom_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.reservation
    ADD CONSTRAINT reservation_classroom_id_fkey FOREIGN KEY (classroom_id) REFERENCES public.classroom(id);


--
-- TOC entry 3061 (class 2606 OID 25259)
-- Name: reservation reservation_created_by_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.reservation
    ADD CONSTRAINT reservation_created_by_id_fkey FOREIGN KEY (created_by_id) REFERENCES public."user"(id);


--
-- TOC entry 3062 (class 2606 OID 25313)
-- Name: schedule schedule_class_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.schedule
    ADD CONSTRAINT schedule_class_id_fkey FOREIGN KEY (class_id) REFERENCES public.class(id) ON DELETE CASCADE;


--
-- TOC entry 3063 (class 2606 OID 25318)
-- Name: schedule schedule_classroom_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.schedule
    ADD CONSTRAINT schedule_classroom_id_fkey FOREIGN KEY (classroom_id) REFERENCES public.classroom(id);


--
-- TOC entry 3064 (class 2606 OID 25323)
-- Name: schedule schedule_reservation_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.schedule
    ADD CONSTRAINT schedule_reservation_id_fkey FOREIGN KEY (reservation_id) REFERENCES public.reservation(id);


--
-- TOC entry 3056 (class 2606 OID 25206)
-- Name: subjectbuildinglink subjectbuildinglink_building_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.subjectbuildinglink
    ADD CONSTRAINT subjectbuildinglink_building_id_fkey FOREIGN KEY (building_id) REFERENCES public.building(id);


--
-- TOC entry 3057 (class 2606 OID 25211)
-- Name: subjectbuildinglink subjectbuildinglink_subject_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.subjectbuildinglink
    ADD CONSTRAINT subjectbuildinglink_subject_id_fkey FOREIGN KEY (subject_id) REFERENCES public.subject(id);


--
-- TOC entry 3042 (class 2606 OID 25008)
-- Name: user user_created_by_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."user"
    ADD CONSTRAINT user_created_by_id_fkey FOREIGN KEY (created_by_id) REFERENCES public."user"(id);


--
-- TOC entry 3058 (class 2606 OID 25221)
-- Name: userbuildinglink userbuildinglink_building_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.userbuildinglink
    ADD CONSTRAINT userbuildinglink_building_id_fkey FOREIGN KEY (building_id) REFERENCES public.building(id);


--
-- TOC entry 3059 (class 2606 OID 25226)
-- Name: userbuildinglink userbuildinglink_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.userbuildinglink
    ADD CONSTRAINT userbuildinglink_user_id_fkey FOREIGN KEY (user_id) REFERENCES public."user"(id);


--
-- TOC entry 3240 (class 0 OID 0)
-- Dependencies: 6
-- Name: SCHEMA public; Type: ACL; Schema: -; Owner: postgres
--

REVOKE USAGE ON SCHEMA public FROM PUBLIC;
GRANT ALL ON SCHEMA public TO PUBLIC;


-- Completed on 2024-11-07 14:52:02 -03

--
-- PostgreSQL database dump complete
--

