-- Exemplo de schema base; ajuste conforme seu domínio.
CREATE TABLE IF NOT EXISTS bets (
    id SERIAL PRIMARY KEY,
    source VARCHAR(50) NOT NULL,
    event VARCHAR(200) NOT NULL,
    market VARCHAR(100) NOT NULL,
    odd NUMERIC(10,4) NOT NULL,
    captured_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS analyses (
    id SERIAL PRIMARY KEY,
    bet_id INT NOT NULL REFERENCES bets(id) ON DELETE CASCADE,
    signal VARCHAR(50) NOT NULL,
    confidence NUMERIC(5,2) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);
