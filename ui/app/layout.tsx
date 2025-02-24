import './globals.css'
import { GeistSans } from 'geist/font/sans'
import { cn } from '@/lib/utils'

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className={cn(
        "min-h-screen bg-background font-sans antialiased",
        GeistSans.className
      )}>
        {children}
      </body>
    </html>
  )
}