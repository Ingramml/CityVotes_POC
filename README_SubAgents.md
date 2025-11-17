# CityVotes POC Sub-Agents

Simple sub-agent architecture for the CityVotes proof of concept, supporting Santa Ana and Pomona voting data visualization.

## 🎯 Sub-Agents Overview

This POC implements **2 simple sub-agents** to demonstrate the sub-agent pattern without unnecessary complexity:

### 1. Data Validation Agent (`agents/data_validation_agent.py`)
- **Purpose**: Validate uploaded JSON voting data files
- **Key Functions**:
  - `validate_json()` - Main validation method
  - `validate_vote_structure()` - Check required fields
  - `validate_member_votes()` - Validate member voting data
  - `get_validation_summary()` - Get data overview

### 2. City Configuration Agent (`agents/city_config_agent.py`)
- **Purpose**: Manage city-specific settings and council member info
- **Key Functions**:
  - `get_city_config()` - Get complete city configuration
  - `get_supported_cities()` - List available cities
  - `validate_member_name()` - Check if member exists in city roster
  - `get_city_colors()` - Get city-specific color schemes

## 🚀 Quick Start

### Test the Agents
```bash
# Test individual agents
python3 agents/data_validation_agent.py
python3 agents/city_config_agent.py

# Test integration
python3 test_agents.py
```

### Run Flask Example
```bash
# Install Flask
pip install Flask

# Run the demo
python3 flask_example.py
```

Then visit: http://127.0.0.1:5000

## 📊 Expected Data Structure

The agents expect JSON files with this structure:

```json
{
  "votes": [
    {
      "agenda_item_number": "7.1",
      "agenda_item_title": "Budget Amendment",
      "outcome": "Pass",
      "tally": {
        "ayes": 5,
        "noes": 2,
        "abstain": 0,
        "absent": 0
      },
      "member_votes": {
        "Mayor Valerie Amezcua": "Aye",
        "Vince Sarmiento": "Aye",
        "Phil Bacerra": "Nay"
      }
    }
  ]
}
```

## 🏛️ Configured Cities

### Santa Ana, CA
- **Council Size**: 7 members
- **Colors**: Blue (#1f4e79) and Gold (#f4b942)
- **Members**: Mayor Valerie Amezcua, Vince Sarmiento, Phil Bacerra, Johnathan Ryan Hernandez, Thai Viet Phan, Benjamin Vazquez, David Penaloza

### Pomona, CA
- **Council Size**: 5 members (placeholder)
- **Colors**: Green (#2c5530) and Gold (#ffd700)
- **Members**: Placeholder configuration

## 🔧 Flask Integration Example

The `flask_example.py` demonstrates how to use both sub-agents in a web application:

```python
from agents import DataValidationAgent, CityConfigAgent

# Initialize sub-agents
data_validator = DataValidationAgent()
city_config = CityConfigAgent()

@app.route('/upload', methods=['POST'])
def upload_file():
    # Step 1: Validate with Data Validation Agent
    is_valid, errors = data_validator.validate_json(file_data, city)

    # Step 2: Get city info from City Configuration Agent
    city_cfg = city_config.get_city_config(city)

    # Step 3: Return results
    return jsonify({'success': is_valid, 'errors': errors})
```

## 📋 API Endpoints

The Flask example provides these endpoints:

- `GET /` - Demo interface
- `GET /api/cities` - Get supported cities
- `GET /api/city/<name>` - Get city configuration
- `POST /upload` - Upload and validate JSON file
- `POST /api/validate` - Validate JSON via API

## ✅ Benefits for POC

### Simple Architecture
- Only 2 sub-agents vs. 5 complex ones
- Clear separation of concerns
- Easy to understand and extend

### Immediate Value
- Validates Santa Ana data right away
- Supports multi-city configuration
- Prevents bad data from reaching dashboard

### Future-Proof
- Easy to add new cities (just update config)
- Can promote regular functions to sub-agents later
- Modular design supports scaling

## 🧪 Testing

### Unit Tests
```bash
# Each agent has built-in tests
python3 agents/data_validation_agent.py  # Shows validation test
python3 agents/city_config_agent.py      # Shows config test
```

### Integration Test
```bash
# Test both agents working together
python3 test_agents.py
```

### Expected Output
```
✓ Data Validation Agent: Working
✓ City Configuration Agent: Working
✓ Agent Communication: Working
✓ Error Handling: Working
```

## 📝 Next Steps

1. **Use the agents** in your main Flask application
2. **Test with real Santa Ana data** files
3. **Add Pomona configuration** when data becomes available
4. **Promote functions to sub-agents** as needed (chart generation, data processing)

## 🎯 POC Focus

This implementation prioritizes:
- **Simplicity** over complexity
- **Working code** over extensive features
- **Learning** the sub-agent pattern
- **Foundation** for future scaling

Perfect for a 2-week proof of concept timeline!