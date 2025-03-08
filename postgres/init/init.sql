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

CREATE TABLE IF NOT EXISTS public.weather_data(
	weather_data_id serial NOT NULL PRIMARY KEY,
	created_at timestamptz NULL,
	updated_at timestamptz NULL,
	forecast_time timestamptz NULL UNIQUE,
	temp numeric NULL,
	hum numeric NULL,
	sky_status varchar(6) NULL,
	lightning_strike numeric NULL,
	wind_direction numeric NULL,
	wind_speed numeric NULL,
	rainfall numeric NULL,
	rainfall_type varchar(6) NULL,
	east_west_wind_component numeric NULL,
	south_north_wind_component numeric NULL
);

ALTER TABLE public.weather_data 
ADD CONSTRAINT weather_data_forecast_time_unique UNIQUE (forecast_time);

COMMENT ON COLUMN public.weather_data.created_at IS '생성 시간';
COMMENT ON COLUMN public.weather_data.forecast_time IS '예보 시간';
COMMENT ON COLUMN public.weather_data.temp IS '기온 (℃)';
COMMENT ON COLUMN public.weather_data.hum IS '습도 (%)';
COMMENT ON COLUMN public.weather_data.sky_status  IS '하늘상태 (Code 501)';
COMMENT ON COLUMN public.weather_data.lightning_strike IS '낙뢰 (kA)';
COMMENT ON COLUMN public.weather_data.wind_direction IS '풍향 (deg)';
COMMENT ON COLUMN public.weather_data.wind_speed IS '풍속 (m/s)';
COMMENT ON COLUMN public.weather_data.rainfall IS '시간당 강우량 (mm)';
COMMENT ON COLUMN public.weather_data.rainfall_type IS '강수 형태(Code 502)';
COMMENT ON COLUMN public.weather_data.east_west_wind_component IS '동서바람성분 (m/s): 동(+표기), 서(-표기)';
COMMENT ON COLUMN public.weather_data.south_north_wind_component IS '남북바람성분 (m/s) 북(+표기), 남(-표기)';