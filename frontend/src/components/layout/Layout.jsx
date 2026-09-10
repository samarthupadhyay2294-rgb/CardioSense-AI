import React from 'react'
import { Outlet } from 'react-router-dom'
import Navbar from './Navbar'
import Footer from './Footer'

function Layout() {
  return (
    <div className="flex min-h-screen flex-col">
      <Navbar />
      <main className="flex-1 pt-20">
        <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6">
          <Outlet />
        </div>
      </main>
      <Footer />
    </div>
  )
}

export default Layout
