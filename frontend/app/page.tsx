'use client'

import { motion } from 'framer-motion'
import { useEffect, useRef } from 'react'


export default function LandingPage() {
  const canvasRef = useRef<HTMLCanvasElement>(null)

  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas) return

    const ctx = canvas.getContext('2d')
    if (!ctx) return

    canvas.width = window.innerWidth
    canvas.height = window.innerHeight

    const dots: Dot[] = []
    const dotCount = 100

    class Dot {
      x: number
      y: number
      size: number
      speedX: number
      speedY: number

      constructor() {
        this.x = Math.random() * canvas.width
        this.y = Math.random() * canvas.height
        this.size = Math.random() * 3 + 2 // Increased size range
        this.speedX = (Math.random() - 0.5) * 0.5
        this.speedY = (Math.random() - 0.5) * 0.5
      }

      update() {
        this.x += this.speedX
        this.y += this.speedY

        if (this.x < 0 || this.x > canvas.width) this.speedX *= -1
        if (this.y < 0 || this.y > canvas.height) this.speedY *= -1
      }

      draw() {
        if (!ctx) return
        ctx.fillStyle = 'rgba(99, 102, 241, 0.3)' // Increased opacity
        ctx.beginPath()
        ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2)
        ctx.fill()
      }
    }

    for (let i = 0; i < dotCount; i++) {
      dots.push(new Dot())
    }

    function animate() {
      if (!ctx) return
      ctx.clearRect(0, 0, canvas.width, canvas.height)
      dots.forEach(dot => {
        dot.update()
        dot.draw()
      })
      requestAnimationFrame(animate)
    }

    animate()

    const handleResize = () => {
      if (!canvas) return
      canvas.width = window.innerWidth
      canvas.height = window.innerHeight
    }

    window.addEventListener('resize', handleResize)

    return () => {
      window.removeEventListener('resize', handleResize)
    }
  }, [])

  return (
    <div className={`relative flex flex-col justify-between h-screen w-full overflow-hidden bg-gradient-to-br from-blue-50 via-indigo-100 to-purple-100`}>
      <canvas ref={canvasRef} className="absolute inset-0 z-0" />
      <div className="relative z-10 self-end p-8">
        <a
          className="rounded-full bg-gradient-to-r from-indigo-500 to-purple-500 px-6 py-2 text-lg font-semibold text-white shadow-lg transition-all hover:from-indigo-600 hover:to-purple-600 hover:shadow-xl focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2"
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.4 }}
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
        >
          Get Started
        </a>
      </div>
      
      <div className="relative z-10 p-8 mb-8 ml-8">
        <motion.div
          className="flex flex-col items-start"
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.8, delay: 0.2 }}
        >
          <h1 className="text-6xl font-bold text-indigo-900 sm:text-7xl md:text-8xl lg:text-9xl">
            RAG
          </h1>
          <p className="mt-2 text-2xl font-medium text-indigo-700 sm:text-3xl md:text-4xl">
            on your
          </p>
          <p className="mt-2 bg-gradient-to-r from-indigo-600 via-purple-600 to-pink-600 bg-clip-text text-4xl font-bold text-transparent sm:text-5xl md:text-6xl lg:text-7xl">
            OpenAPI
          </p>
          <p className="bg-gradient-to-r from-indigo-600 via-purple-600 to-pink-600 bg-clip-text text-4xl font-bold text-transparent sm:text-5xl md:text-6xl lg:text-7xl">
            Specification
          </p>
        </motion.div>
      </div>
    </div>
  )
}