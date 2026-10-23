import { createSlice, createAsyncThunk } from '@reduxjs/toolkit'
import api from '../utils/api'
import { mergeFormUpdates, setStatus } from './investigationSlice'

export const sendMessage = createAsyncThunk(
  'chat/sendMessage',
  async ({ message, investigationId, history }, { dispatch, rejectWithValue }) => {
    try {
      dispatch(setStatus('extracting'))
      const { data } = await api.post('/api/chat', {
        message,
        investigation_id: investigationId || null,
        history: history || [],
      })
      if (data.form_updates) {
        dispatch(mergeFormUpdates(data.form_updates))
      }
      if (data.investigation) {
        dispatch(mergeFormUpdates(data.investigation))
      }
      dispatch(setStatus('ready'))
      return data
    } catch (err) {
      dispatch(setStatus('idle'))
      return rejectWithValue(err.response?.data?.detail || err.message)
    }
  }
)

export const uploadDocument = createAsyncThunk(
  'chat/uploadDocument',
  async ({ file, investigationId }, { dispatch, rejectWithValue }) => {
    try {
      dispatch(setStatus('extracting'))
      const form = new FormData()
      form.append('file', file)
      if (investigationId) form.append('investigation_id', investigationId)

      const { data } = await api.post('/api/upload', form, {
        headers: { 'Content-Type': 'multipart/form-data' },
      })
      if (data.investigation) {
        dispatch(mergeFormUpdates(data.investigation))
      }
      dispatch(setStatus('ready'))
      return data
    } catch (err) {
      dispatch(setStatus('idle'))
      return rejectWithValue(err.response?.data?.detail || err.message)
    }
  }
)

const chatSlice = createSlice({
  name: 'chat',
  initialState: {
    messages: [
      {
        role: 'assistant',
        content:
          'Ready to open a new investigation. Paste a deviation description, email body, or upload a PDF. I will extract the data, run structured RCA (5 Whys + Fishbone), surface missing evidence, and propose CAPA recommendations.',
      },
    ],
    loading: false,
    error: null,
  },
  reducers: {
    addMessage(state, action) {
      state.messages.push(action.payload)
    },
    clearChat(state) {
      state.messages = [
        {
          role: 'assistant',
          content:
            'Ready to open a new investigation. Paste a deviation description, email body, or upload a PDF.',
        },
      ]
      state.error = null
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(sendMessage.pending, (state) => {
        state.loading = true
        state.error = null
      })
      .addCase(sendMessage.fulfilled, (state, action) => {
        state.loading = false
        state.messages.push({ role: 'assistant', content: action.payload.reply })
      })
      .addCase(sendMessage.rejected, (state, action) => {
        state.loading = false
        state.error = action.payload
        state.messages.push({
          role: 'assistant',
          content: `I encountered an issue: ${action.payload}. Please check the Groq API key and try again.`,
        })
      })
      .addCase(uploadDocument.pending, (state) => {
        state.loading = true
        state.error = null
      })
      .addCase(uploadDocument.fulfilled, (state, action) => {
        state.loading = false
        state.messages.push({
          role: 'assistant',
          content: action.payload.reply || 'Document processed and form updated.',
        })
      })
      .addCase(uploadDocument.rejected, (state, action) => {
        state.loading = false
        state.error = action.payload
        state.messages.push({
          role: 'assistant',
          content: `Upload failed: ${action.payload}`,
        })
      })
  },
})

export const { addMessage, clearChat } = chatSlice.actions
export default chatSlice.reducer
