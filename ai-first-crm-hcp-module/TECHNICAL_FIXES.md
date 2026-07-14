# AI First CRM HCP Module - Technical Fixes Guide with Code Examples

## Critical Production Blockers - Solutions

### 1. Fix Database Session Injection in Agent Router

**Problem**: Tools decorated with `@tool` won't receive database session parameter

**Location**: `backend/app/routers/agent.py` line 130+

**Current Broken Code**:
```python
# This won't work - db will always be None
@tool
def log_interaction(
    hcp_name: str,
    discussion: str,
    db: Session = None  # ❌ LangChain won't inject this
):
    if db is None:
        return {"success": False}  # ❌ Always fails

# In router:
result = log_interaction.invoke({
    "hcp_name": extracted.get("doctor_name"),
    "discussion": request.message,
    "db": db  # ❌ Not injected by @tool decorator
})
```

**Solution Option 1: Use Tool Executor Pattern**
```python
# backend/app/agents/hcp_agent.py
from langgraph.prebuilt import ToolExecutor

# Create tools with database context
def create_tools(db: Session):
    """Create tools with database session injected"""
    
    @tool
    def log_interaction_impl(
        hcp_name: str,
        discussion: str,
        interaction_type: str = "call",
        interaction_date: str = None,
        summary: str = None,
        follow_up_date: str = None,
        hospital: str = None,
    ):
        """Tool implementation - db passed via closure"""
        return log_interaction_handler(
            db=db,  # ✅ Database injected via closure
            hcp_name=hcp_name,
            discussion=discussion,
            interaction_type=interaction_type,
            interaction_date=interaction_date,
            summary=summary,
            follow_up_date=follow_up_date,
            hospital=hospital
        )
    
    return [log_interaction_impl]

# In router:
@router.post("/chat", response_model=AgentChatResponse)
async def agent_chat(request: AgentChatRequest, db: Session = Depends(get_db)):
    # Create tools with db session
    tools = create_tools(db)
    
    # Create agent graph with tools
    tool_node = ToolNode(tools)
    
    # Run agent
    agent_result = run_hcp_agent(
        request.message,
        conversation_history,
        tools=tools,
        db=db
    )
```

**Solution Option 2: Use State Context**
```python
# Pass database through agent state
from langgraph.graph import StateGraph

class AgentState(TypedDict):
    user_input: str
    db: Session  # ✅ Pass db in state
    conversation_history: List[BaseMessage]

def execute_log_interaction(state: AgentState):
    """Tool handler - db available from state"""
    db = state["db"]  # ✅ Get db from state
    
    hcp_service = HCPService(db)
    interaction_service = InteractionService(db)
    
    # ... use db to save interaction
    
    return state

# In router:
state = {
    "user_input": request.message,
    "db": db,  # ✅ Pass db in state
    "conversation_history": conversation_history
}
result = graph.invoke(state)
```

**Recommended Implementation**:
```python
# backend/app/tools/log_interaction_handler.py
def log_interaction_handler(
    db: Session,
    hcp_name: str,
    discussion: str,
    interaction_type: str = "call",
    interaction_date: str = None,
    summary: str = None,
    follow_up_date: str = None,
    hospital: str = None,
) -> Dict[str, Any]:
    """
    Core logic that doesn't rely on @tool decorator
    This can be called from tools or directly
    """
    if db is None:
        return {"success": False, "message": "Database session required"}
    
    try:
        # Set default date if not provided
        if interaction_date is None:
            interaction_date = datetime.now().isoformat()
        
        # Parse dates
        try:
            parsed_date = datetime.fromisoformat(interaction_date.replace('Z', '+00:00'))
        except (ValueError, AttributeError):
            parsed_date = datetime.now()
        
        # Generate summary if not provided
        if not summary:
            summary = generate_summary_from_discussion(discussion)
        
        # Initialize services
        hcp_service = HCPService(db)
        interaction_service = InteractionService(db)
        
        # Look up or create HCP
        hcp = hcp_service.get_hcp_by_name(hcp_name.strip())
        
        if hcp is None:
            # Create new HCP with unique email
            hcp_create_data = HCPCreate(
                doctor_name=hcp_name.strip(),
                hospital=hospital or "Unknown Hospital",
                specialization="General",
                city="Unknown",
                phone="000-000-0000",
                email=f"hcp_{uuid.uuid4().hex[:8]}@aifirst-crm.local"  # ✅ Unique
            )
            hcp = hcp_service.create_hcp(hcp_create_data)
        
        # Create interaction
        interaction_data = InteractionCreate(
            hcp_id=hcp.id,
            interaction_date=parsed_date,
            discussion=discussion.strip(),
            summary=summary.strip(),
            follow_up_date=parsed_follow_up if follow_up_date else None
        )
        
        interaction = interaction_service.create_interaction(interaction_data)
        db.commit()  # ✅ Explicit commit
        
        return {
            "success": True,
            "interaction_id": interaction.id,
            "doctor_name": hcp.doctor_name,
            "message": f"Interaction logged successfully for {hcp.doctor_name}"
        }
        
    except Exception as e:
        db.rollback()  # ✅ Rollback on error
        logger.error(f"Failed to log interaction: {str(e)}", exc_info=True)
        return {
            "success": False,
            "message": f"Failed to log interaction: {str(e)}"
        }

# In router:
from app.tools.log_interaction_handler import log_interaction_handler

@router.post("/chat", response_model=AgentChatResponse)
async def agent_chat(request: AgentChatRequest, db: Session = Depends(get_db)):
    # ... existing code ...
    
    if selected_tool == "log_interaction":
        result = log_interaction_handler(
            db=db,  # ✅ Pass db directly
            hcp_name=extracted.get("doctor_name"),
            discussion=request.message,
            # ... other params
        )
        interaction_id = result.get("interaction_id")
```

---

### 2. Fix Search Interactions - Replace Mock Data

**Problem**: `search_interactions` tool returns mock data, never queries database

**Location**: `backend/app/tools/search_interactions.py`

**Current Broken Code**:
```python
@tool
def search_interactions(
    hcp_id: int = None,
    hcp_name: str = None,
    date_from: str = None,
    date_to: str = None,
    interaction_type: str = None,
    limit: int = 10,
    db: Session = None  # ❌ Same db injection problem
) -> Dict[str, Any]:
    # Build search criteria but never use it
    search_criteria = {"limit": limit}
    
    # ❌ Returns mock data
    mock_results = generate_mock_results(search_criteria)
    
    return {
        "success": True,
        "results": mock_results  # ❌ Never queries database
    }

def generate_mock_results(criteria):
    """Mock data - should be removed"""
    return [
        {"id": 1, "hcp_name": "Dr. Sarah Johnson", ...},
        {"id": 2, "hcp_name": "Dr. Michael Chen", ...},
    ]
```

**Fixed Implementation**:
```python
# backend/app/tools/search_interactions_handler.py
from datetime import datetime
from typing import Dict, List, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from app.models.interaction import Interaction
from app.models.hcp import HCP

def search_interactions_handler(
    db: Session,
    hcp_id: int = None,
    hcp_name: str = None,
    date_from: str = None,
    date_to: str = None,
    interaction_type: str = None,
    limit: int = 10
) -> Dict[str, Any]:
    """
    Query database for interactions matching criteria.
    """
    if db is None:
        return {"success": False, "message": "Database session required"}
    
    try:
        # Start with base query
        query = db.query(Interaction).join(HCP)
        
        # Apply filters
        filters = []
        
        # Filter by HCP ID
        if hcp_id:
            filters.append(Interaction.hcp_id == hcp_id)
        
        # Filter by HCP name (case-insensitive partial match)
        if hcp_name:
            filters.append(HCP.doctor_name.ilike(f"%{hcp_name}%"))
        
        # Filter by date range
        if date_from:
            try:
                parsed_date_from = datetime.fromisoformat(
                    date_from.replace('Z', '+00:00')
                )
                filters.append(Interaction.interaction_date >= parsed_date_from)
            except (ValueError, AttributeError):
                pass
        
        if date_to:
            try:
                parsed_date_to = datetime.fromisoformat(
                    date_to.replace('Z', '+00:00')
                )
                filters.append(Interaction.interaction_date <= parsed_date_to)
            except (ValueError, AttributeError):
                pass
        
        # Filter by interaction type (if model has this field)
        # Note: Current model doesn't have type field, add if needed
        
        # Apply all filters
        if filters:
            query = query.filter(and_(*filters))
        
        # Get total count before limiting
        total = query.count()
        
        # Sort by date descending and apply limit
        results = query.order_by(
            Interaction.interaction_date.desc()
        ).limit(limit).all()
        
        # Format results
        formatted_results = []
        for interaction in results:
            formatted_results.append({
                "id": interaction.id,
                "hcp_id": interaction.hcp_id,
                "hcp_name": interaction.hcp.doctor_name,
                "hospital": interaction.hcp.hospital,
                "interaction_date": interaction.interaction_date.isoformat(),
                "discussion": interaction.discussion[:200] + "..." if len(interaction.discussion) > 200 else interaction.discussion,
                "summary": interaction.summary,
                "follow_up_date": interaction.follow_up_date.isoformat() if interaction.follow_up_date else None,
            })
        
        return {
            "success": True,
            "message": f"Found {len(formatted_results)} interactions",
            "total": total,
            "results": formatted_results
        }
        
    except Exception as e:
        logger.error(f"Search interactions failed: {str(e)}", exc_info=True)
        return {
            "success": False,
            "message": f"Search failed: {str(e)}",
            "results": []
        }
```

**In Router**:
```python
# backend/app/routers/agent.py
from app.tools.search_interactions_handler import search_interactions_handler

# Inside agent_chat function
if selected_tool == "search_interactions":
    # Extract search params from user message or structured data
    result = search_interactions_handler(
        db=db,
        hcp_id=extracted_hcp_id,
        hcp_name=extracted_hcp_name,
        date_from=start_date,
        date_to=end_date,
        limit=10
    )
    
    # Format results for user-friendly response
    if result.get("success") and result.get("results"):
        reply = f"Found {result['total']} interactions:\n\n"
        for r in result["results"]:
            reply += f"- {r['hcp_name']} ({r['interaction_date']}): {r['summary']}\n"
```

---

### 3. Fix Login Authentication - Replace Demo Mode

**Problem**: Demo login with fake JWT token won't work with real backend

**Location**: `frontend/src/pages/Login.tsx`

**Current Broken Code**:
```typescript
const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    // ❌ Simulates API call, doesn't call real backend
    setTimeout(() => {
        if (email && password) {
            dispatch(
                loginSuccess({
                    user: {
                        id: '1',
                        name: 'John Doe',
                        email: email,
                        role: 'Sales Representative',
                    },
                    token: 'fake-jwt-token',  // ❌ Not valid
                })
            );
            // ❌ Token not sent in API requests
            navigate('/dashboard');
        } else {
            setError('Please fill in all fields');
        }
        setLoading(false);
    }, 1000);  // ❌ No real API call
};
```

**Fixed Implementation**:
```typescript
// frontend/src/pages/Login.tsx
import axios from 'axios';

const Login: React.FC = () => {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);

    const dispatch = useDispatch();
    const navigate = useNavigate();
    const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

    const validateEmail = (email: string): boolean => {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setError('');
        setLoading(true);

        // ✅ Validation
        if (!email || !password) {
            setError('Please fill in all fields');
            setLoading(false);
            return;
        }

        if (!validateEmail(email)) {
            setError('Please enter a valid email address');
            setLoading(false);
            return;
        }

        if (password.length < 6) {
            setError('Password must be at least 6 characters');
            setLoading(false);
            return;
        }

        try {
            // ✅ Call real backend API
            const response = await axios.post(
                `${API_BASE_URL}/auth/login`,  // Endpoint must be implemented in backend
                {
                    email,
                    password
                },
                {
                    headers: {
                        'Content-Type': 'application/json'
                    }
                }
            );

            const { access_token, token_type, user } = response.data;

            // ✅ Store token (consider using httpOnly cookie)
            localStorage.setItem('token', access_token);
            localStorage.setItem('token_type', token_type || 'Bearer');
            localStorage.setItem('token_expiry', 
                (Date.now() + 30 * 60 * 1000).toString()  // 30 minutes default
            );

            // ✅ Dispatch Redux action with real user data
            dispatch(
                loginSuccess({
                    user: {
                        id: user.id,
                        name: user.name,
                        email: user.email,
                        role: user.role || 'Sales Representative',
                    },
                    token: access_token,
                })
            );

            // ✅ Setup axios interceptor to include token in future requests
            setupAuthInterceptor(access_token);

            navigate('/dashboard');
        } catch (err: unknown) {
            if (axios.isAxiosError(err)) {
                // Handle specific error responses
                if (err.response?.status === 401) {
                    setError('Invalid email or password');
                } else if (err.response?.status === 429) {
                    setError('Too many login attempts. Please try again later.');
                } else {
                    setError(err.response?.data?.detail || 'Login failed');
                }
            } else {
                setError('Network error. Please check your connection.');
            }
            console.error('Login error:', err);
        } finally {
            setLoading(false);
        }
    };

    return (
        <Box
            sx={{
                minHeight: '100vh',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
            }}
        >
            <Container maxWidth="sm">
                <Card sx={{ borderRadius: 3, boxShadow: '0 8px 32px rgba(0,0,0,0.1)' }}>
                    <CardContent sx={{ p: 4 }}>
                        <Box sx={{ textAlign: 'center', mb: 4 }}>
                            <Typography variant="h4" component="h1" gutterBottom sx={{ fontWeight: 600 }}>
                                AI First CRM
                            </Typography>
                            <Typography variant="body2" color="text.secondary">
                                HCP Module Login
                            </Typography>
                        </Box>

                        {error && (
                            <Alert severity="error" sx={{ mb: 3 }}>
                                {error}
                            </Alert>
                        )}

                        <form onSubmit={handleSubmit}>
                            <TextField
                                fullWidth
                                label="Email"
                                type="email"
                                value={email}
                                onChange={(e) => setEmail(e.target.value)}
                                margin="normal"
                                required
                                autoComplete="email"
                                autoFocus
                                disabled={loading}
                                error={!!error && !validateEmail(email)}
                            />
                            <TextField
                                fullWidth
                                label="Password"
                                type="password"
                                value={password}
                                onChange={(e) => setPassword(e.target.value)}
                                margin="normal"
                                required
                                autoComplete="current-password"
                                disabled={loading}
                            />
                            <Button
                                type="submit"
                                fullWidth
                                variant="contained"
                                size="large"
                                sx={{ mt: 3, mb: 2 }}
                                disabled={loading}
                            >
                                {loading ? <CircularProgress size={24} /> : 'Sign In'}
                            </Button>
                        </form>

                        <Box sx={{ mt: 3, textAlign: 'center' }}>
                            <Typography variant="body2" color="text.secondary">
                                Don't have an account?{' '}
                                <Link href="/register" underline="hover">
                                    Sign up here
                                </Link>
                            </Typography>
                        </Box>
                    </CardContent>
                </Card>
            </Container>
        </Box>
    );
};

// ✅ Setup axios interceptor
const setupAuthInterceptor = (token: string) => {
    axios.interceptors.request.use(
        (config) => {
            const storedToken = localStorage.getItem('token');
            if (storedToken) {
                config.headers.Authorization = `Bearer ${storedToken}`;
            }
            return config;
        },
        (error) => Promise.reject(error)
    );

    // Handle token expiry
    axios.interceptors.response.use(
        (response) => response,
        (error) => {
            if (error.response?.status === 401) {
                // Token expired or invalid
                localStorage.removeItem('token');
                window.location.href = '/login';
            }
            return Promise.reject(error);
        }
    );
};

export default Login;
```

**Backend Auth Endpoint** (needs to be implemented):
```python
# backend/app/routers/auth.py
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext

router = APIRouter(prefix="/auth", tags=["Authentication"])

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

@router.post("/login")
def login(
    email: str,
    password: str,
    db: Session = Depends(get_db)
):
    """
    User login endpoint - validates credentials and returns JWT token
    """
    # TODO: Query user from database
    # TODO: Verify password
    # TODO: Generate JWT token
    # TODO: Return token and user data
    pass

@router.post("/register")
def register(
    email: str,
    password: str,
    name: str,
    db: Session = Depends(get_db)
):
    """User registration endpoint"""
    pass
```

---

### 4. Fix Redux Integration - HCPList Component

**Problem**: Component uses mock data instead of Redux + API

**Location**: `frontend/src/pages/HCPList.tsx`

**Current Broken Code**:
```typescript
// ❌ Hardcoded mock data
const mockHCPs: HCP[] = [
    {
        id: '1',
        name: 'Dr. Sarah Johnson',
        // ... more mock data
    },
    // ... more mock HCPs
];

const HCPList: React.FC = () => {
    // ❌ Local state, no Redux
    const [selectedHCP, setSelectedHCP] = useState<HCP | null>(null);

    // ❌ Uses mock data directly
    const filteredHCPs = mockHCPs.filter(
        (hcp) => hcp.name.toLowerCase().includes(searchTerm.toLowerCase())
    );
```

**Fixed Implementation**:
```typescript
// frontend/src/pages/HCPList.tsx
import React, { useState, useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { AppDispatch, RootState } from '../store/store';
import { fetchHCPs, setSelectedHCP } from '../store/slices/hcpSlice';
import { debounce } from 'lodash';

interface HCP {
    id: number;
    doctor_name: string;
    hospital: string;
    specialization: string;
    email: string;
    phone: string;
    city: string;
    status?: 'active' | 'inactive';
}

const HCPList: React.FC = () => {
    const [searchTerm, setSearchTerm] = useState('');
    const [skip, setSkip] = useState(0);
    const [limit, setLimit] = useState(10);

    const dispatch = useDispatch<AppDispatch>();
    
    // ✅ Get data from Redux
    const { hcps, selectedHCP, loading, error } = useSelector(
        (state: RootState) => state.hcp
    );

    // ✅ Fetch data on mount and when filters change
    useEffect(() => {
        dispatch(fetchHCPs({ skip, limit, search: searchTerm }));
    }, [dispatch, skip, limit, searchTerm]);

    // ✅ Debounced search to avoid too many requests
    const handleSearch = debounce((value: string) => {
        setSearchTerm(value);
        setSkip(0);  // Reset to first page on new search
    }, 500);

    const handleView = (hcp: HCP) => {
        // ✅ Use Redux instead of local state
        dispatch(setSelectedHCP(hcp));
    };

    const handleAddHCP = () => {
        // Navigate to add HCP form
        // Dispatch action to open modal or navigate to create page
    };

    const handleEdit = (hcp: HCP) => {
        // Dispatch action to edit HCP
    };

    if (error) {
        return (
            <Box sx={{ flexGrow: 1 }}>
                <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
                    <Alert severity="error">
                        Error loading HCPs: {error}
                        <Button onClick={() => dispatch(fetchHCPs({ skip, limit, search: searchTerm }))}>
                            Retry
                        </Button>
                    </Alert>
                </Container>
            </Box>
        );
    }

    return (
        <Box sx={{ flexGrow: 1 }}>
            <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 4 }}>
                    <Typography variant="h4" sx={{ fontWeight: 600 }}>
                        HCP List
                    </Typography>
                    <Button
                        variant="contained"
                        startIcon={<AddIcon />}
                        sx={{ borderRadius: 2 }}
                        onClick={handleAddHCP}
                    >
                        Add HCP
                    </Button>
                </Box>

                <Paper sx={{ p: 3, mb: 3 }}>
                    <Box sx={{ display: 'flex', gap: 2, alignItems: 'center' }}>
                        <TextField
                            fullWidth
                            placeholder="Search HCPs by name, specialty, organization, or city..."
                            onChange={(e) => handleSearch(e.target.value)}
                            InputProps={{
                                startAdornment: <SearchIcon sx={{ mr: 1, color: 'text.secondary' }} />,
                            }}
                            sx={{ maxWidth: 600 }}
                            disabled={loading}
                        />
                    </Box>
                </Paper>

                {loading ? (
                    <LoadingSpinner message="Loading HCPs..." />
                ) : (
                    <TableContainer component={Paper}>
                        <Table>
                            <TableHead>
                                <TableRow sx={{ backgroundColor: '#f5f5f5' }}>
                                    <TableCell sx={{ fontWeight: 600 }}>Name</TableCell>
                                    <TableCell sx={{ fontWeight: 600 }}>Specialty</TableCell>
                                    <TableCell sx={{ fontWeight: 600 }}>Organization</TableCell>
                                    <TableCell sx={{ fontWeight: 600 }}>City</TableCell>
                                    <TableCell sx={{ fontWeight: 600 }}>Email</TableCell>
                                    <TableCell sx={{ fontWeight: 600 }}>Phone</TableCell>
                                    <TableCell sx={{ fontWeight: 600 }}>Actions</TableCell>
                                </TableRow>
                            </TableHead>
                            <TableBody>
                                {hcps && hcps.length > 0 ? (
                                    hcps.map((hcp) => (
                                        <TableRow key={hcp.id} hover>
                                            <TableCell sx={{ fontWeight: 500 }}>{hcp.doctor_name}</TableCell>
                                            <TableCell>{hcp.specialization}</TableCell>
                                            <TableCell>{hcp.hospital}</TableCell>
                                            <TableCell>{hcp.city}</TableCell>
                                            <TableCell>{hcp.email}</TableCell>
                                            <TableCell>{hcp.phone}</TableCell>
                                            <TableCell>
                                                <IconButton 
                                                    size="small" 
                                                    onClick={() => handleView(hcp)}
                                                    title="View"
                                                >
                                                    <VisibilityIcon />
                                                </IconButton>
                                                <IconButton 
                                                    size="small" 
                                                    onClick={() => handleEdit(hcp)}
                                                    title="Edit"
                                                >
                                                    <EditIcon />
                                                </IconButton>
                                            </TableCell>
                                        </TableRow>
                                    ))
                                ) : (
                                    <TableRow>
                                        <TableCell colSpan={7} align="center" sx={{ py: 4 }}>
                                            No HCPs found
                                        </TableCell>
                                    </TableRow>
                                )}
                            </TableBody>
                        </Table>
                    </TableContainer>
                )}

                {/* Pagination */}
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mt: 4 }}>
                    <Button
                        disabled={skip === 0}
                        onClick={() => setSkip(Math.max(0, skip - limit))}
                    >
                        Previous
                    </Button>
                    <Typography>
                        Page {Math.floor(skip / limit) + 1}
                    </Typography>
                    <Button
                        disabled={!hcps || hcps.length < limit}
                        onClick={() => setSkip(skip + limit)}
                    >
                        Next
                    </Button>
                </Box>

                {/* View/Edit Dialog */}
                <Dialog
                    open={!!selectedHCP}
                    onClose={() => dispatch(setSelectedHCP(null))}
                    maxWidth="sm"
                    fullWidth
                >
                    <DialogTitle>HCP Details</DialogTitle>
                    <DialogContent>
                        {selectedHCP && (
                            <Box sx={{ pt: 2, display: 'flex', flexDirection: 'column', gap: 2 }}>
                                <Typography><strong>Name:</strong> {selectedHCP.doctor_name}</Typography>
                                <Typography><strong>Specialty:</strong> {selectedHCP.specialization}</Typography>
                                <Typography><strong>Hospital:</strong> {selectedHCP.hospital}</Typography>
                                <Typography><strong>City:</strong> {selectedHCP.city}</Typography>
                                <Typography><strong>Email:</strong> {selectedHCP.email}</Typography>
                                <Typography><strong>Phone:</strong> {selectedHCP.phone}</Typography>
                            </Box>
                        )}
                    </DialogContent>
                    <DialogActions>
                        <Button onClick={() => dispatch(setSelectedHCP(null))}>Close</Button>
                        <Button variant="contained">Edit</Button>
                    </DialogActions>
                </Dialog>
            </Container>
        </Box>
    );
};

export default HCPList;
```

**Updated hcpSlice with async thunks**:
```typescript
// frontend/src/store/slices/hcpSlice.ts
import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import { hcpApi, HCPResponse } from '../../services/hcpApi';

interface HCP extends HCPResponse {}

interface HCPState {
    hcps: HCP[];
    selectedHCP: HCP | null;
    loading: boolean;
    error: string | null;
    total: number;
}

const initialState: HCPState = {
    hcps: [],
    selectedHCP: null,
    loading: false,
    error: null,
    total: 0,
};

// ✅ Async thunk to fetch HCPs
export const fetchHCPs = createAsyncThunk(
    'hcp/fetchHCPs',
    async (
        params: { skip?: number; limit?: number; search?: string },
        { rejectWithValue }
    ) => {
        try {
            const response = await hcpApi.getHCPs(
                params.skip || 0,
                params.limit || 10,
                params.search
            );
            return response;
        } catch (error: unknown) {
            return rejectWithValue(
                error instanceof Error ? error.message : 'Failed to fetch HCPs'
            );
        }
    }
);

// ✅ Async thunk to create HCP
export const createHCP = createAsyncThunk(
    'hcp/createHCP',
    async (hcpData: any, { rejectWithValue }) => {
        try {
            return await hcpApi.createHCP(hcpData);
        } catch (error: unknown) {
            return rejectWithValue(
                error instanceof Error ? error.message : 'Failed to create HCP'
            );
        }
    }
);

const hcpSlice = createSlice({
    name: 'hcp',
    initialState,
    reducers: {
        setSelectedHCP: (state, action: PayloadAction<HCP | null>) => {
            state.selectedHCP = action.payload;
        },
        clearError: (state) => {
            state.error = null;
        },
    },
    extraReducers: (builder) => {
        builder
            // Fetch HCPs
            .addCase(fetchHCPs.pending, (state) => {
                state.loading = true;
                state.error = null;
            })
            .addCase(fetchHCPs.fulfilled, (state, action) => {
                state.loading = false;
                state.hcps = action.payload.hcps;
                state.total = action.payload.total;
            })
            .addCase(fetchHCPs.rejected, (state, action) => {
                state.loading = false;
                state.error = (action.payload as string) || 'Failed to fetch HCPs';
            })
            // Create HCP
            .addCase(createHCP.pending, (state) => {
                state.loading = true;
                state.error = null;
            })
            .addCase(createHCP.fulfilled, (state, action) => {
                state.loading = false;
                state.hcps.unshift(action.payload);
            })
            .addCase(createHCP.rejected, (state, action) => {
                state.loading = false;
                state.error = (action.payload as string) || 'Failed to create HCP';
            });
    },
});

export const { setSelectedHCP, clearError } = hcpSlice.actions;
export default hcpSlice.reducer;
```

---

### 5. Fix Configuration Security Issues

**Problem**: Hardcoded CORS origins and unvalidated secrets

**Location**: `backend/app/core/config.py`

**Current Broken Code**:
```python
# ❌ Hardcoded values
CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]

# ❌ Not validated
SECRET_KEY: str
DEBUG: bool = True
```

**Fixed Implementation**:
```python
# backend/app/core/config.py
import os
from pydantic import Field, validator
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = Field(..., description="Database connection URL")
    TEST_DATABASE_URL: str = Field(default="sqlite:///:memory:")
    
    # Application
    APP_NAME: str = Field(default="AI First CRM HCP Module")
    APP_VERSION: str = Field(default="1.0.0")
    ENVIRONMENT: str = Field(default="development")  # ✅ Add environment
    DEBUG: bool = Field(default=False)  # ✅ Default to False
    
    SECRET_KEY: str = Field(..., min_length=32, description="JWT secret key")
    ALGORITHM: str = Field(default="HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30)
    
    # CORS - ✅ From environment variable
    CORS_ORIGINS: str = Field(
        default="http://localhost:3000,http://127.0.0.1:3000",
        description="Comma-separated list of allowed CORS origins"
    )
    
    # Server
    HOST: str = Field(default="0.0.0.0")
    PORT: int = Field(default=8000)
    
    # Groq API
    GROQ_API_KEY: str = Field(..., description="Groq API key")
    GROQ_MODEL: str = Field(default="gemma2-9b-it")
    
    class Config:
        env_file = ".env"
        case_sensitive = True
    
    # ✅ Validators
    @validator('DEBUG')
    def validate_debug(cls, v):
        if v and os.getenv('ENVIRONMENT') == 'production':
            raise ValueError('DEBUG must be False in production')
        return v
    
    @validator('SECRET_KEY')
    def validate_secret_key(cls, v):
        if len(v) < 32:
            raise ValueError('SECRET_KEY must be at least 32 characters')
        if not any(c.isupper() for c in v):
            raise ValueError('SECRET_KEY must contain uppercase letters')
        if not any(c.isdigit() for c in v):
            raise ValueError('SECRET_KEY must contain digits')
        return v
    
    @validator('GROQ_API_KEY')
    def validate_groq_api_key(cls, v):
        if not v.startswith('gsk_'):
            raise ValueError('Invalid GROQ_API_KEY format')
        if len(v) < 20:
            raise ValueError('GROQ_API_KEY appears to be invalid')
        return v
    
    @property
    def cors_origins_list(self) -> List[str]:
        """Parse CORS origins from comma-separated string"""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(',') if origin.strip()]


# ✅ Validate settings on import
settings = Settings()

# Log configuration (without secrets)
if settings.ENVIRONMENT == 'development':
    import logging
    logger = logging.getLogger(__name__)
    logger.info(f"Settings loaded: environment={settings.ENVIRONMENT}, debug={settings.DEBUG}")
```

**Update main.py to use parsed CORS**:
```python
# backend/app/main.py
from app.core.config import settings

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,  # ✅ Use parsed list
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**Environment file**:
```bash
# .env
ENVIRONMENT=development
DEBUG=false

DATABASE_URL=postgresql+psycopg://user:password@localhost:5432/ai_crm_hcp
TEST_DATABASE_URL=sqlite:///:memory:

SECRET_KEY=aBc123!@#DeFgHiJkLmNoPqRsTuVwXyZ123  # ✅ Min 32 chars with mix
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000,https://yourdomain.com

HOST=0.0.0.0
PORT=8000

GROQ_API_KEY=gsk_your_actual_api_key_here
GROQ_MODEL=gemma2-9b-it
```

---

## Summary of Fixes Applied

| Issue | Severity | File | Fix Type |
|-------|----------|------|----------|
| Database session in tools | 🔴 Critical | agent.py, tools | Refactor to pass db via state/context |
| Mock search data | 🔴 Critical | search_interactions.py | Query database instead |
| Fake JWT auth | 🔴 Critical | Login.tsx | Implement real auth endpoint |
| Hardcoded CORS | 🔴 Critical | config.py | Use environment variables |
| HCP list mock data | 🔴 Critical | HCPList.tsx | Use Redux + API |
| Incomplete files | 🔴 Critical | Multiple | Complete implementations |
| No validation | 🟠 Major | config.py | Add pydantic validators |
| Missing Redux thunks | 🟠 Major | hcpSlice.ts | Add async thunks |
| Type safety | 🟠 Major | authSlice.ts | Remove `any` types |
| Error handling | 🟠 Major | Multiple | Add proper error handlers |

---

**Next Steps**:
1. Apply these fixes in order of criticality
2. Test each fix thoroughly
3. Update integration tests
4. Deploy to staging environment
5. Run end-to-end tests
6. Deploy to production
