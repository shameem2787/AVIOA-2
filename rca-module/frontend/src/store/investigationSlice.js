import { createSlice, createAsyncThunk } from '@reduxjs/toolkit'
import api from '../utils/api'

const initialState = {
  current: null,
  list: [],
  loading: false,
  error: null,
  status: 'idle', // idle | extracting | ready | saving
}

export const fetchInvestigations = createAsyncThunk(
  'investigation/fetchAll',
  async () => {
    const { data } = await api.get('/api/investigations')
    return data
  }
)

export const createInvestigation = createAsyncThunk(
  'investigation/create',
  async (payload) => {
    const { data } = await api.post('/api/investigations', payload)
    return data
  }
)

export const updateInvestigation = createAsyncThunk(
  'investigation/update',
  async ({ id, updates }) => {
    const { data } = await api.patch(`/api/investigations/${id}`, updates)
    return data
  }
)

export const commitInvestigation = createAsyncThunk(
  'investigation/commit',
  async (id) => {
    const { data } = await api.post(`/api/investigations/${id}/commit`)
    return data
  }
)

const investigationSlice = createSlice({
  name: 'investigation',
  initialState,
  reducers: {
    setCurrent(state, action) {
      state.current = action.payload
    },
    mergeFormUpdates(state, action) {
      if (!state.current) {
        state.current = { id: null, status: 'Under Investigation', ...action.payload }
      } else {
        state.current = { ...state.current, ...action.payload }
      }
      state.status = 'ready'
    },
    clearCurrent(state) {
      state.current = null
      state.status = 'idle'
    },
    setStatus(state, action) {
      state.status = action.payload
    },
    updateLocalField(state, action) {
      const { path, value } = action.payload
      if (!state.current) return
      // Simple top-level for now; nested handled carefully
      const keys = path.split('.')
      if (keys.length === 1) {
        state.current[keys[0]] = value
      } else {
        // shallow nested support
        let obj = state.current
        for (let i = 0; i < keys.length - 1; i++) {
          if (!obj[keys[i]]) obj[keys[i]] = {}
          obj = obj[keys[i]]
        }
        obj[keys[keys.length - 1]] = value
      }
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchInvestigations.fulfilled, (state, action) => {
        state.list = action.payload
      })
      .addCase(createInvestigation.fulfilled, (state, action) => {
        state.current = action.payload
        state.list.unshift(action.payload)
      })
      .addCase(updateInvestigation.fulfilled, (state, action) => {
        state.current = action.payload
      })
      .addCase(commitInvestigation.fulfilled, (state, action) => {
        state.current = action.payload
      })
  },
})

export const {
  setCurrent,
  mergeFormUpdates,
  clearCurrent,
  setStatus,
  updateLocalField,
} = investigationSlice.actions

export default investigationSlice.reducer
