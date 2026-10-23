import { configureStore } from '@reduxjs/toolkit'
import investigationReducer from './investigationSlice'
import chatReducer from './chatSlice'

export const store = configureStore({
  reducer: {
    investigation: investigationReducer,
    chat: chatReducer,
  },
})
