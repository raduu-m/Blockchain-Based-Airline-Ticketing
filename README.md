# Blockchain-Based Airline Ticketing System

## Overview

This project is a blockchain-based airline ticketing system that ensures secure and verifiable transactions for ticket issuance and transfers. The backend is built using Rust with the Actix Web framework, while the frontend is implemented using Streamlit (`app.py`).

## Features

- **User Account Creation**: Register and manage user accounts.
- **Mint NFT-Based Airline Tickets**: Each airline ticket is an NFT stored on a blockchain.
- **Transfer Tickets**: Users can transfer tickets to other accounts securely.
- **View User-Owned Tickets**: Retrieve a list of NFTs owned by a specific account.
- **Blockchain Security**: Each transaction (minting, transfer) is recorded on the blockchain, ensuring transparency and immutability.

## Tech Stack

### Backend (Rust & Actix Web)

- `actix_web`: For building the REST API.
- `chrono`: For timestamping blockchain transactions.
- `sha2`: For cryptographic hashing.
- `serde`: For JSON serialization/deserialization.
- `hex`: For encoding hashes.
- `std::sync::Mutex`: For managing shared state in a thread-safe manner.

### Frontend (Streamlit)

- `streamlit`: Web-based UI for interacting with the blockchain API.
- `requests`: To communicate with the backend.

## Installation

### Prerequisites

Ensure you have the following installed:

- Rust and Cargo
- Python (>=3.8)
- Streamlit (`pip install streamlit`)


## Running the Backend

```bash
cargo run
```

The Actix Web server will start at `http://127.0.0.1:8080`.

## Running the Frontend

```bash
streamlit run app.py
```

This will launch the Streamlit app in your web browser.

## API Endpoints

| Endpoint                      | Method | Description                              |
| ----------------------------- | ------ | ---------------------------------------- |
| `/accounts`                   | `POST` | Create a new user account                |
| `/nfts`                       | `POST` | Mint a new airline ticket (NFT)          |
| `/accounts/{account_id}/nfts` | `GET`  | Get all NFTs owned by a user             |
| `/nfts/transfer`              | `POST` | Transfer an NFT from one user to another |

## Example Usage

### Creating an Account

```bash
curl -X POST http://127.0.0.1:8080/accounts -H "Content-Type: application/json" -d '{"id": "user123"}'
```

### Minting a Ticket

```bash
curl -X POST http://127.0.0.1:8080/nfts -H "Content-Type: application/json" -d '{"name": "Flight ABC123", "description": "NYC to LA", "owner": "user123", "metadata": {"id": "doc1", "document_type": 1, "image": "ticket.png", "date_added": "2025-01-29", "profile_type": "passenger"}}'
```

### Viewing User Tickets

```bash
curl -X GET http://127.0.0.1:8080/accounts/user123/nfts
```

### Transferring a Ticket

```bash
curl -X POST http://127.0.0.1:8080/nfts/transfer -H "Content-Type: application/json" -d '{"from": "user123", "to": "user456", "nft_id": "nft_123456"}'
```

## License

This project is licensed under the MIT License.

