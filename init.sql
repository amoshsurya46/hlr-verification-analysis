USE HLRDB;

CREATE TABLE hlr_verification (
    id INT AUTO_INCREMENT PRIMARY KEY,
    operation VARCHAR(50),
    bss_msisdn VARCHAR(20),
    bss_imsi VARCHAR(20),
    hlr_msisdn VARCHAR(50),
    hlr_imsi VARCHAR(50),
    file_name VARCHAR(100),
    record_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);