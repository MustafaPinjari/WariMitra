/**
 * Home page
 */
export default function Home() {
  return (
    <main className="min-h-screen p-4">
      <div className="max-w-7xl mx-auto">
        <h1 className="text-4xl font-bold mb-8">WariMitra</h1>
        <p className="text-xl text-gray-300">Real-time emergency response and medical coordination system</p>
        
        <div className="mt-8 grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-gray-800 p-6 rounded">
            <h2 className="text-2xl font-bold mb-2">SOS Portal</h2>
            <p className="text-gray-400">Emergency response system</p>
          </div>
          <div className="bg-gray-800 p-6 rounded">
            <h2 className="text-2xl font-bold mb-2">Medical Camps</h2>
            <p className="text-gray-400">Healthcare coordination</p>
          </div>
          <div className="bg-gray-800 p-6 rounded">
            <h2 className="text-2xl font-bold mb-2">Live Tracking</h2>
            <p className="text-gray-400">Real-time GPS monitoring</p>
          </div>
        </div>
      </div>
    </main>
  )
}
