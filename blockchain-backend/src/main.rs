use actix_web::{web, App, HttpResponse, HttpServer, Responder};
use chrono::Utc;
use serde::{Deserialize, Serialize};
use sha2::{Sha256, Digest};
use std::sync::Mutex;
use std::collections::HashMap;

// NFT structure
#[derive(Debug, Clone, Serialize, Deserialize)]
struct NFT {
    id: String,
    name: String,
    description: String,
    owner: String,
    metadata: NftDocument,
    created_at: i64,
}

// Account structure
#[derive(Debug, Clone, Serialize, Deserialize)]
struct Account {
    id: String,
    nfts: Vec<String>, // Store NFT IDs
    created_at: i64,
}

// Request structures
#[derive(Debug, Deserialize)]
struct CreateAccountRequest {
    id: String,
}

#[derive(Debug, Deserialize)]
struct CreateNFTRequest {
    name: String,
    description: String,
    owner: String,
    metadata: NftDocument,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
struct NftDocument{
    id:String,
    document_type:u32,
    image:String,
    date_added:String,
    profile_type:String,
}

#[derive(Debug, Deserialize)]
struct TransferNFTRequest {
    from: String,
    to: String,
    nft_id: String,
}

// Block structure with NFT transactions
#[derive(Debug, Clone, Serialize, Deserialize)]
struct Block {
    index: u64,
    timestamp: i64,
    data: Transaction,
    previous_hash: String,
    hash: String,
    nonce: u64,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
enum Transaction {
    CreateAccount(Account),
    MintNFT(NFT),
    Transfer { nft_id: String, from: String, to: String },
}

// Blockchain structure with accounts and NFTs
#[derive(Debug, Clone)]
struct Blockchain {
    chain: Vec<Block>,
    difficulty: u32,
    accounts: HashMap<String, Account>,
    nfts: HashMap<String, NFT>,
}

// Application state
struct AppState {
    blockchain: Mutex<Blockchain>,
}

impl Block {
    fn new(index: u64, data: Transaction, previous_hash: String) -> Self {
        let timestamp = Utc::now().timestamp();
        let mut block = Block {
            index,
            timestamp,
            data,
            previous_hash,
            hash: String::new(),
            nonce: 0,
        };
        block.hash = block.calculate_hash();
        block
    }

    fn calculate_hash(&self) -> String {
        let mut hasher = Sha256::new();
        let input = format!("{}{}{:?}{}{}", 
            self.index,
            self.timestamp,
            self.data,
            self.previous_hash,
            self.nonce
        );
        hasher.update(input.as_bytes());
        hex::encode(hasher.finalize())
    }

    fn mine_block(&mut self, difficulty: u32) {
        let target = "0".repeat(difficulty as usize);
        while &self.hash[..difficulty as usize] != target {
            self.nonce += 1;
            self.hash = self.calculate_hash();
        }
    }
}

impl Blockchain {
    fn new() -> Self {
        let mut chain = Vec::new();
        let genesis_account = Account {
            id: "genesis".to_string(),
            nfts: vec![],
            created_at: Utc::now().timestamp(),
        };
        
        chain.push(Block::new(
            0,
            Transaction::CreateAccount(genesis_account),
            String::from("0"),
        ));

        Blockchain {
            chain,
            difficulty: 4,
            accounts: HashMap::new(),
            nfts: HashMap::new(),
        }
    }

    fn create_account(&mut self, account_id: String) -> Result<Account, String> {
        if self.accounts.contains_key(&account_id) {
            return Err("Account already exists".to_string());
        }

        let account = Account {
            id: account_id.clone(),
            nfts: vec![],
            created_at: Utc::now().timestamp(),
        };

        let block = Block::new(
            self.chain.len() as u64,
            Transaction::CreateAccount(account.clone()),
            self.chain.last().unwrap().hash.clone(),
        );

        self.accounts.insert(account_id, account.clone());
        self.chain.push(block);
        Ok(account)
    }

    fn mint_nft(&mut self, request: CreateNFTRequest) -> Result<NFT, String> {
        if !self.accounts.contains_key(&request.owner) {
            return Err("Account does not exist".to_string());
        }

        let _metadata = request.metadata;
        println!("Metadata: {:?}", _metadata);

        let nft_id = format!("nft_{}", Utc::now().timestamp());
        let nft = NFT {
            id: nft_id.clone(),
            name: request.name,
            description: request.description,
            owner: request.owner.clone(),
            metadata: _metadata,
            created_at: Utc::now().timestamp(),
        };

        let block = Block::new(
            self.chain.len() as u64,
            Transaction::MintNFT(nft.clone()),
            self.chain.last().unwrap().hash.clone(),
        );

        if let Some(account) = self.accounts.get_mut(&request.owner) {
            account.nfts.push(nft_id.clone());
        }

        self.nfts.insert(nft_id, nft.clone());
        self.chain.push(block);
        Ok(nft)
    }

    fn get_account_nfts(&self, account_id: &str) -> Result<Vec<NFT>, String> {
        match self.accounts.get(account_id) {
            Some(account) => {
                let nfts: Vec<NFT> = account.nfts.iter()
                    .filter_map(|nft_id| self.nfts.get(nft_id))
                    .cloned()
                    .collect();
                Ok(nfts)
            }
            None => Err("Account not found".to_string())
        }
    }

    fn transfer_nft(&mut self, request: TransferNFTRequest) -> Result<NFT, String> {
        // Validate sender account exists
        let from_account = self.accounts.get(&request.from)
            .ok_or("Sender account not found")?;
            
        // Validate receiver account exists
        if !self.accounts.contains_key(&request.to) {
            return Err("Receiver account not found".to_string());
        }

        // Validate NFT exists and belongs to sender
        let nft = self.nfts.get(&request.nft_id)
            .ok_or("NFT not found")?;

        if nft.owner != request.from {
            return Err("NFT does not belong to sender".to_string());
        }

        // Create transfer transaction
        let block = Block::new(
            self.chain.len() as u64,
            Transaction::Transfer {
                nft_id: request.nft_id.clone(),
                from: request.from.clone(),
                to: request.to.clone(),
            },
            self.chain.last().unwrap().hash.clone(),
        );

        // Update NFT ownership
        if let Some(nft) = self.nfts.get_mut(&request.nft_id) {
            nft.owner = request.to.clone();
        }

        // Remove NFT from sender's account
        if let Some(account) = self.accounts.get_mut(&request.from) {
            account.nfts.retain(|id| id != &request.nft_id);
        }

        // Add NFT to receiver's account
        if let Some(account) = self.accounts.get_mut(&request.to) {
            account.nfts.push(request.nft_id.clone());
        }

        self.chain.push(block);
        Ok(self.nfts.get(&request.nft_id).unwrap().clone())
    }
}

// API endpoints
async fn create_account(
    data: web::Data<AppState>,
    request: web::Json<CreateAccountRequest>,
) -> impl Responder {
    let mut blockchain = data.blockchain.lock().unwrap();
    match blockchain.create_account(request.id.clone()) {
        Ok(account) => HttpResponse::Ok().json(account),
        Err(e) => HttpResponse::BadRequest().body(e),
    }
}

async fn mint_nft(
    data: web::Data<AppState>,
    request: web::Json<CreateNFTRequest>,
) -> impl Responder {
    let mut blockchain = data.blockchain.lock().unwrap();
    match blockchain.mint_nft(request.0) {
        Ok(nft) => {
            print!("NFT: {:?}", nft);
            HttpResponse::Ok().json(nft)
        },
        Err(e) => HttpResponse::BadRequest().body(e),
    }
}

// async fn mint_user_doc(
//     data: web::Data<AppState>,
//     request: web::Json<NftDocument>
// ) -> impl Responder {
//     let mut blockchain = data.blockchain.lock().unwrap()
//     match blockchain.mint_nft(request.0) {
//         Ok(nft) => HttpResponse::Ok().json(nft),
//         Err(e) => HttpResponse::BadRequest().body(e),
//     }
// }

async fn get_account_nfts(
    data: web::Data<AppState>,
    account_id: web::Path<String>,
) -> impl Responder {
    let blockchain = data.blockchain.lock().unwrap();
    match blockchain.get_account_nfts(&account_id) {
        Ok(nfts) => HttpResponse::Ok().json(nfts),
        Err(e) => HttpResponse::NotFound().body(e),
    }
}

async fn transfer_nft(
    data: web::Data<AppState>,
    request: web::Json<TransferNFTRequest>,
) -> impl Responder {
    let mut blockchain = data.blockchain.lock().unwrap();
    match blockchain.transfer_nft(request.0) {
        Ok(nft) => HttpResponse::Ok().json(nft),
        Err(e) => HttpResponse::BadRequest().body(e),
    }
}


#[actix_web::main]
async fn main() -> std::io::Result<()> {
    let app_state = web::Data::new(AppState {
        blockchain: Mutex::new(Blockchain::new()),
    });

    println!("Server running at http://localhost:8080");

    HttpServer::new(move || {
        App::new()
            .app_data(app_state.clone())
            .route("/accounts", web::post().to(create_account))
            .route("/nfts", web::post().to(mint_nft))
            .route("/accounts/{account_id}/nfts", web::get().to(get_account_nfts))
            .route("/nfts/transfer", web::post().to(transfer_nft))
    })
    .bind("127.0.0.1:8080")?
    .run()
    .await
}
