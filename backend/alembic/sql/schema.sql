--
-- PostgreSQL database dump
--

\restrict krM9IxfDQU6vnFXxTRj89fvn86UjoAho9cJWO1lolznJUBYEMLxhhhBAsalhdjY

-- Dumped from database version 16.11 (Debian 16.11-1.pgdg13+1)
-- Dumped by pg_dump version 16.10

-- Started on 2025-12-29 11:51:45 UTC

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
-- TOC entry 2 (class 3079 OID 16394)
-- Name: pgcrypto; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS pgcrypto WITH SCHEMA public;


--
-- TOC entry 3534 (class 0 OID 0)
-- Dependencies: 2
-- Name: EXTENSION pgcrypto; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION pgcrypto IS 'cryptographic functions';


SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- TOC entry 216 (class 1259 OID 16389)
-- Name: alembic_version; Type: TABLE; Schema: public; Owner: tenant
--

CREATE TABLE public.alembic_version (
    version_num character varying(32) NOT NULL
);


ALTER TABLE public.alembic_version OWNER TO tenant;

--
-- TOC entry 219 (class 1259 OID 16582)
-- Name: conversations; Type: TABLE; Schema: public; Owner: tenant
--

CREATE TABLE public.conversations (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    tenant_id uuid NOT NULL,
    status text DEFAULT 'open'::text NOT NULL,
    visitor_id text,
    meta jsonb DEFAULT '{}'::jsonb NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.conversations OWNER TO tenant;

--
-- TOC entry 222 (class 1259 OID 16650)
-- Name: events; Type: TABLE; Schema: public; Owner: tenant
--

CREATE TABLE public.events (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    tenant_id uuid NOT NULL,
    conversation_id uuid,
    incident_id uuid,
    event_type text NOT NULL,
    payload jsonb DEFAULT '{}'::jsonb NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.events OWNER TO tenant;

--
-- TOC entry 221 (class 1259 OID 16624)
-- Name: incidents; Type: TABLE; Schema: public; Owner: tenant
--

CREATE TABLE public.incidents (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    tenant_id uuid NOT NULL,
    conversation_id uuid,
    type text NOT NULL,
    severity smallint,
    status text DEFAULT 'open'::text NOT NULL,
    payload jsonb DEFAULT '{}'::jsonb NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.incidents OWNER TO tenant;

--
-- TOC entry 220 (class 1259 OID 16603)
-- Name: messages; Type: TABLE; Schema: public; Owner: tenant
--

CREATE TABLE public.messages (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    tenant_id uuid NOT NULL,
    conversation_id uuid NOT NULL,
    role text NOT NULL,
    content text NOT NULL,
    meta jsonb DEFAULT '{}'::jsonb NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.messages OWNER TO tenant;

--
-- TOC entry 218 (class 1259 OID 16566)
-- Name: tenant_domains; Type: TABLE; Schema: public; Owner: tenant
--

CREATE TABLE public.tenant_domains (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    tenant_id uuid NOT NULL,
    domain text NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.tenant_domains OWNER TO tenant;

--
-- TOC entry 217 (class 1259 OID 16554)
-- Name: tenants; Type: TABLE; Schema: public; Owner: tenant
--

CREATE TABLE public.tenants (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    name text NOT NULL,
    slug text NOT NULL,
    is_active boolean DEFAULT true NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.tenants OWNER TO tenant;

--
-- TOC entry 3350 (class 2606 OID 16393)
-- Name: alembic_version alembic_version_pkc; Type: CONSTRAINT; Schema: public; Owner: tenant
--

ALTER TABLE ONLY public.alembic_version
    ADD CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num);


--
-- TOC entry 3359 (class 2606 OID 16593)
-- Name: conversations conversations_pkey; Type: CONSTRAINT; Schema: public; Owner: tenant
--

ALTER TABLE ONLY public.conversations
    ADD CONSTRAINT conversations_pkey PRIMARY KEY (id);


--
-- TOC entry 3374 (class 2606 OID 16659)
-- Name: events events_pkey; Type: CONSTRAINT; Schema: public; Owner: tenant
--

ALTER TABLE ONLY public.events
    ADD CONSTRAINT events_pkey PRIMARY KEY (id);


--
-- TOC entry 3368 (class 2606 OID 16635)
-- Name: incidents incidents_pkey; Type: CONSTRAINT; Schema: public; Owner: tenant
--

ALTER TABLE ONLY public.incidents
    ADD CONSTRAINT incidents_pkey PRIMARY KEY (id);


--
-- TOC entry 3366 (class 2606 OID 16612)
-- Name: messages messages_pkey; Type: CONSTRAINT; Schema: public; Owner: tenant
--

ALTER TABLE ONLY public.messages
    ADD CONSTRAINT messages_pkey PRIMARY KEY (id);


--
-- TOC entry 3356 (class 2606 OID 16574)
-- Name: tenant_domains tenant_domains_pkey; Type: CONSTRAINT; Schema: public; Owner: tenant
--

ALTER TABLE ONLY public.tenant_domains
    ADD CONSTRAINT tenant_domains_pkey PRIMARY KEY (id);


--
-- TOC entry 3352 (class 2606 OID 16564)
-- Name: tenants tenants_pkey; Type: CONSTRAINT; Schema: public; Owner: tenant
--

ALTER TABLE ONLY public.tenants
    ADD CONSTRAINT tenants_pkey PRIMARY KEY (id);


--
-- TOC entry 3363 (class 2606 OID 16595)
-- Name: conversations uq_conversations__tenant_id__id; Type: CONSTRAINT; Schema: public; Owner: tenant
--

ALTER TABLE ONLY public.conversations
    ADD CONSTRAINT uq_conversations__tenant_id__id UNIQUE (tenant_id, id);


--
-- TOC entry 3372 (class 2606 OID 16637)
-- Name: incidents uq_incidents__tenant_id__id; Type: CONSTRAINT; Schema: public; Owner: tenant
--

ALTER TABLE ONLY public.incidents
    ADD CONSTRAINT uq_incidents__tenant_id__id UNIQUE (tenant_id, id);


--
-- TOC entry 3360 (class 1259 OID 16601)
-- Name: ix_conversations__tenant_id__created_at; Type: INDEX; Schema: public; Owner: tenant
--

CREATE INDEX ix_conversations__tenant_id__created_at ON public.conversations USING btree (tenant_id, created_at);


--
-- TOC entry 3361 (class 1259 OID 16602)
-- Name: ix_conversations__tenant_id__status; Type: INDEX; Schema: public; Owner: tenant
--

CREATE INDEX ix_conversations__tenant_id__status ON public.conversations USING btree (tenant_id, status);


--
-- TOC entry 3375 (class 1259 OID 16675)
-- Name: ix_events__tenant_id__created_at; Type: INDEX; Schema: public; Owner: tenant
--

CREATE INDEX ix_events__tenant_id__created_at ON public.events USING btree (tenant_id, created_at);


--
-- TOC entry 3376 (class 1259 OID 16676)
-- Name: ix_events__tenant_id__event_type__created_at; Type: INDEX; Schema: public; Owner: tenant
--

CREATE INDEX ix_events__tenant_id__event_type__created_at ON public.events USING btree (tenant_id, event_type, created_at);


--
-- TOC entry 3369 (class 1259 OID 16648)
-- Name: ix_incidents__tenant_id__created_at; Type: INDEX; Schema: public; Owner: tenant
--

CREATE INDEX ix_incidents__tenant_id__created_at ON public.incidents USING btree (tenant_id, created_at);


--
-- TOC entry 3370 (class 1259 OID 16649)
-- Name: ix_incidents__tenant_id__status; Type: INDEX; Schema: public; Owner: tenant
--

CREATE INDEX ix_incidents__tenant_id__status ON public.incidents USING btree (tenant_id, status);


--
-- TOC entry 3364 (class 1259 OID 16623)
-- Name: ix_messages__tenant_id__conversation_id__created_at; Type: INDEX; Schema: public; Owner: tenant
--

CREATE INDEX ix_messages__tenant_id__conversation_id__created_at ON public.messages USING btree (tenant_id, conversation_id, created_at);


--
-- TOC entry 3354 (class 1259 OID 16581)
-- Name: ix_tenant_domains__tenant_id; Type: INDEX; Schema: public; Owner: tenant
--

CREATE INDEX ix_tenant_domains__tenant_id ON public.tenant_domains USING btree (tenant_id);


--
-- TOC entry 3357 (class 1259 OID 16580)
-- Name: uq_tenant_domains__domain; Type: INDEX; Schema: public; Owner: tenant
--

CREATE UNIQUE INDEX uq_tenant_domains__domain ON public.tenant_domains USING btree (domain);


--
-- TOC entry 3353 (class 1259 OID 16565)
-- Name: uq_tenants__slug; Type: INDEX; Schema: public; Owner: tenant
--

CREATE UNIQUE INDEX uq_tenants__slug ON public.tenants USING btree (slug);


--
-- TOC entry 3378 (class 2606 OID 16596)
-- Name: conversations fk_conversations__tenant_id__tenants; Type: FK CONSTRAINT; Schema: public; Owner: tenant
--

ALTER TABLE ONLY public.conversations
    ADD CONSTRAINT fk_conversations__tenant_id__tenants FOREIGN KEY (tenant_id) REFERENCES public.tenants(id) ON DELETE CASCADE;


--
-- TOC entry 3383 (class 2606 OID 16660)
-- Name: events fk_events__tenant_id__tenants; Type: FK CONSTRAINT; Schema: public; Owner: tenant
--

ALTER TABLE ONLY public.events
    ADD CONSTRAINT fk_events__tenant_id__tenants FOREIGN KEY (tenant_id) REFERENCES public.tenants(id) ON DELETE CASCADE;


--
-- TOC entry 3384 (class 2606 OID 16665)
-- Name: events fk_events__tenant_id_conversation_id__conversations; Type: FK CONSTRAINT; Schema: public; Owner: tenant
--

ALTER TABLE ONLY public.events
    ADD CONSTRAINT fk_events__tenant_id_conversation_id__conversations FOREIGN KEY (tenant_id, conversation_id) REFERENCES public.conversations(tenant_id, id) ON DELETE SET NULL;


--
-- TOC entry 3385 (class 2606 OID 16670)
-- Name: events fk_events__tenant_id_incident_id__incidents; Type: FK CONSTRAINT; Schema: public; Owner: tenant
--

ALTER TABLE ONLY public.events
    ADD CONSTRAINT fk_events__tenant_id_incident_id__incidents FOREIGN KEY (tenant_id, incident_id) REFERENCES public.incidents(tenant_id, id) ON DELETE SET NULL;


--
-- TOC entry 3381 (class 2606 OID 16638)
-- Name: incidents fk_incidents__tenant_id__tenants; Type: FK CONSTRAINT; Schema: public; Owner: tenant
--

ALTER TABLE ONLY public.incidents
    ADD CONSTRAINT fk_incidents__tenant_id__tenants FOREIGN KEY (tenant_id) REFERENCES public.tenants(id) ON DELETE CASCADE;


--
-- TOC entry 3382 (class 2606 OID 16643)
-- Name: incidents fk_incidents__tenant_id_conversation_id__conversations; Type: FK CONSTRAINT; Schema: public; Owner: tenant
--

ALTER TABLE ONLY public.incidents
    ADD CONSTRAINT fk_incidents__tenant_id_conversation_id__conversations FOREIGN KEY (tenant_id, conversation_id) REFERENCES public.conversations(tenant_id, id) ON DELETE SET NULL;


--
-- TOC entry 3379 (class 2606 OID 16613)
-- Name: messages fk_messages__tenant_id__tenants; Type: FK CONSTRAINT; Schema: public; Owner: tenant
--

ALTER TABLE ONLY public.messages
    ADD CONSTRAINT fk_messages__tenant_id__tenants FOREIGN KEY (tenant_id) REFERENCES public.tenants(id) ON DELETE CASCADE;


--
-- TOC entry 3380 (class 2606 OID 16618)
-- Name: messages fk_messages__tenant_id_conversation_id__conversations; Type: FK CONSTRAINT; Schema: public; Owner: tenant
--

ALTER TABLE ONLY public.messages
    ADD CONSTRAINT fk_messages__tenant_id_conversation_id__conversations FOREIGN KEY (tenant_id, conversation_id) REFERENCES public.conversations(tenant_id, id) ON DELETE CASCADE;


--
-- TOC entry 3377 (class 2606 OID 16575)
-- Name: tenant_domains fk_tenant_domains__tenant_id__tenants; Type: FK CONSTRAINT; Schema: public; Owner: tenant
--

ALTER TABLE ONLY public.tenant_domains
    ADD CONSTRAINT fk_tenant_domains__tenant_id__tenants FOREIGN KEY (tenant_id) REFERENCES public.tenants(id) ON DELETE CASCADE;


-- Completed on 2025-12-29 11:51:45 UTC

--
-- PostgreSQL database dump complete
--

\unrestrict krM9IxfDQU6vnFXxTRj89fvn86UjoAho9cJWO1lolznJUBYEMLxhhhBAsalhdjY

