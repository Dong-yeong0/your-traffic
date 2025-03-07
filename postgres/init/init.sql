CREATE EXTENSION postgis;

CREATE OR REPLACE FUNCTION UPDATE_GEOM()
RETURNS TRIGGER AS $$
BEGIN
    NEW.GEOM = ST_SetSRID(ST_MakePoint(NEW.LONGITUDE, NEW.LATITUDE), 4326);
    RETURN NEW;    
END;
$$ LANGUAGE PLPGSQL;

CREATE TABLE public.unit (
	unit_id varchar(50) NOT NULL,
	unit_name varchar(100) NULL,
	agency_code varchar(10) NULL,
	route_id varchar(20) NULL,
	center_code varchar(10) NULL,
	tcs_branch_code varchar(10) NULL,
	unit_type_code varchar(10) NULL,
	unit_method_code varchar(10) NULL,
	phone_number varchar(20) NULL,
	is_operational_office bool NULL,
	entrance_lane_count int4 NULL,
	exit_lane_count int4 NULL,
	variable_lane_count int4 NULL,
	is_last_private_ic bool NULL,
	is_virtual_office bool NULL,
	CONSTRAINT unit_pkey PRIMARY KEY (unit_id)
);

CREATE TABLE public.unit_location (
	unit_location_id serial4 NOT NULL,
	route_id varchar(10) NULL,
	unit_name varchar(50) NULL,
	route_name varchar(50) NULL,
	latitude numeric(10, 6) NULL,
	longitude numeric(10, 6) NULL,
	"label" varchar(50) NULL,
	geom public.geometry(point, 4326) NULL,
	CONSTRAINT unit_location_pkey PRIMARY KEY (unit_location_id)
);

CREATE TRIGGER SET_GEOM_TRIGGER
BEFORE INSERT OR UPDATE ON PUBLIC.UNIT_LOCATION
FOR EACH ROW
EXECUTE FUNCTION UPDATE_GEOM();

CREATE TABLE public.traffic_data (
	tm_type int4 NOT NULL,
	traffic_amount int4 NOT NULL,
	ex_div_code varchar(10) NOT NULL,
	ex_div_name varchar(50) NOT NULL,
	open_cl_type int4 NOT NULL,
	open_cl_name varchar(50) NOT NULL,
	inout_type int4 NOT NULL,
	inout_name varchar(50) NOT NULL,
	tm_name varchar(50) NOT NULL,
	tcs_type varchar(10) NOT NULL,
	tcs_name varchar(50) NOT NULL,
	car_type int4 NOT NULL,
	region_code varchar(10) NOT NULL,
	region_name varchar(50) NOT NULL,
	sum_date timestamptz NOT NULL,
	created_at timestamptz DEFAULT CURRENT_TIMESTAMP NULL,
	updated_at timestamptz DEFAULT CURRENT_TIMESTAMP NULL,
	CONSTRAINT traffic_data_pkey PRIMARY KEY (sum_date, region_code, tm_type, tcs_type, car_type, inout_type, open_cl_type, ex_div_code)
);

CREATE TABLE public.traffic_data_by_unit (
	unit_name varchar NULL,
	unit_code varchar NOT NULL,
	std_date timestamptz NOT NULL,
	traffic_amount int4 NULL,
	inout_name varchar NOT NULL,
	center_code varchar NULL,
	center_name varchar NULL,
	sum_tm_unit_type_code varchar NULL,
	start_end_std_type_code varchar NULL,
	tcs_car_type_cd varchar NOT NULL,
	brof_code varchar NULL,
	brof_name varchar NULL,
	tcs_car_type_nm varchar NULL,
	tcs_car_type_grp_nm varchar NULL,
	tcs_car_type_grp_cd varchar NULL,
	created_at timestamptz DEFAULT now() NULL,
	updated_at timestamptz DEFAULT now() NULL,
	CONSTRAINT traffic_data_by_unit_pk PRIMARY KEY (unit_code, std_date, inout_name, tcs_car_type_cd)
);

